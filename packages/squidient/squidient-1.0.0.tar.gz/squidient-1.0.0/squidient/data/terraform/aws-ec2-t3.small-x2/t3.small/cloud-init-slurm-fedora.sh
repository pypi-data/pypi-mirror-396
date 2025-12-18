#!/bin/bash
set -eux

# ------------------------------------------------------------
# Role and topology (filled by Terraform via templatefile)
# ------------------------------------------------------------
ROLE="${ROLE}"
HEAD_HOSTNAME="${HEAD_HOSTNAME}"
COMPUTE_HOSTNAME="${COMPUTE_HOSTNAME}"
HEAD_PRIVATE_IP="${HEAD_PRIVATE_IP}"
COMPUTE_NODE_LIST="${COMPUTE_NODE_LIST}"

# ------------------------------------------------------------
# Hostname setup
# ------------------------------------------------------------
if [ "${ROLE}" = "head" ]; then
  hostnamectl set-hostname "${HEAD_HOSTNAME}"
else
  hostnamectl set-hostname "${COMPUTE_HOSTNAME}"
fi

HOSTNAME="$(hostname)"

# ------------------------------------------------------------
# Basic networking
# ------------------------------------------------------------
if [ "${ROLE}" = "head" ]; then
  HEAD_IP="$(hostname -I | awk '{print $1}')"
  if ! grep -q " ${HEAD_HOSTNAME}\b" /etc/hosts; then
    echo "$HEAD_IP ${HEAD_HOSTNAME}" >> /etc/hosts
  fi
else
  if [ -n "${HEAD_PRIVATE_IP}" ] && ! grep -q " ${HEAD_HOSTNAME}\b" /etc/hosts; then
    echo "${HEAD_PRIVATE_IP} ${HEAD_HOSTNAME}" >> /etc/hosts
  fi
  COMPUTE_IP="$(hostname -I | awk '{print $1}')"
  if [ -n "$COMPUTE_IP" ] && ! grep -q " ${COMPUTE_HOSTNAME}\b" /etc/hosts; then
    echo "$COMPUTE_IP ${COMPUTE_HOSTNAME}" >> /etc/hosts
  fi
fi

# ------------------------------------------------------------
# Install base packages
# ------------------------------------------------------------
dnf -y update

dnf -y install \
  slurm slurm-slurmctld slurm-slurmd \
  munge munge-libs munge-devel \
  cmake gcc gcc-c++ gcc-gfortran \
  git make perl wget \
  python3 python3-pip \
  diffutils which \
  tar gzip bzip2 \
  zlib-devel openssl-devel \
  libibverbs rdma-core \
  numactl numactl-devel \
  environment-modules \
  nfs-utils

chmod 755 /
chmod 755 /var
chmod 755 /var/lib

# ------------------------------------------------------------
# NFS server + client handling (durci)
# ------------------------------------------------------------
mkdir -p /shared

if [ "${ROLE}" = "head" ]; then

  chmod 777 /shared

  cat >/etc/exports <<EOF
/shared *(rw,sync,no_subtree_check,no_root_squash,fsid=0)
EOF

  systemctl enable nfs-idmapd || true
  systemctl start  nfs-idmapd || true

  exportfs -ra

  systemctl enable --now nfs-server

  # Script background : rafraîchissement NodeAddr
  cat >/usr/local/sbin/refresh-slurm-nodeaddrs.sh << 'EOS'
#!/bin/bash
set -eux

HEAD_HOSTNAME="slurm-head"
HEAD_IP="$(hostname -I | awk '{print $1}')"

# Wait for slurmctld
for i in $(seq 1 60); do
  if systemctl is-active --quiet slurmctld; then break; fi
  sleep 2
done

# Ensure head is in /etc/hosts
if ! grep -q " $HEAD_HOSTNAME\b" /etc/hosts; then
  echo "$HEAD_IP $HEAD_HOSTNAME" >> /etc/hosts
fi

# Detect compute *.ip files
for i in $(seq 1 60); do
  found_any=false

  for ipfile in /shared/*.ip; do
    [ -e "$ipfile" ] || continue
    found_any=true

    node="$(basename "$ipfile" .ip)"
    ip="$(awk '{print $1}' "$ipfile")"

    [ -n "$ip" ] || continue

    if ! grep -q " $node\b" /etc/hosts; then
      echo "$ip $node" >> /etc/hosts
    fi

    scontrol update NodeName="$node" NodeAddr="$ip" || true
  done

  if $found_any; then exit 0; fi
  sleep 3
done

exit 0
EOS

  chmod +x /usr/local/sbin/refresh-slurm-nodeaddrs.sh
  nohup /usr/local/sbin/refresh-slurm-nodeaddrs.sh >/var/log/refresh-slurm-nodeaddrs.log 2>&1 &

else
  # Client NFS durci
  if [ -n "${HEAD_PRIVATE_IP}" ]; then

    if ! grep -q "/shared " /etc/fstab; then
      echo "${HEAD_PRIVATE_IP}:/shared /shared nfs vers=3,noac,actimeo=0,timeo=600,retrans=5,_netdev 0 0" >> /etc/fstab
    fi

    for i in $(seq 1 40); do
      if mountpoint -q /shared; then break; fi

      mount -t nfs -o vers=3,noac,actimeo=0,timeo=600,retrans=5 "${HEAD_PRIVATE_IP}:/shared" /shared && break || true
      mount -t nfs -o vers=4 "${HEAD_PRIVATE_IP}:/shared" /shared && break || true

      sleep 3
    done

    if mountpoint -q /shared; then
      COMPUTE_IP="$(hostname -I | awk '{print $1}')"
      echo "$COMPUTE_IP" > "/shared/${COMPUTE_HOSTNAME}.ip" || true
    fi
  fi
fi

# ------------------------------------------------------------
# Munge setup
# ------------------------------------------------------------
mkdir -p /etc/munge /var/lib/munge /var/log/munge

if [ "${ROLE}" = "head" ]; then
  if [ ! -f /etc/munge/munge.key ]; then
    if command -v create-munge-key >/dev/null 2>&1; then
      create-munge-key
    else
      dd if=/dev/urandom bs=1 count=1024 of=/etc/munge/munge.key
    fi
  fi
  cp /etc/munge/munge.key /shared/munge.key || true
else
  for i in $(seq 1 30); do
    if [ -f /shared/munge.key ]; then
      cp /shared/munge.key /etc/munge/munge.key
      break
    fi
    sleep 2
  done

  if [ ! -f /etc/munge/munge.key ]; then
    if command -v create-munge-key >/dev/null 2>&1; then
      create-munge-key
    else
      dd if=/dev/urandom bs=1 count=1024 of=/etc/munge/munge.key
    fi
  fi
fi

chown munge:munge /etc/munge/munge.key
chmod 600 /etc/munge/munge.key
chown -R munge:munge /etc/munge /var/lib/munge /var/log/munge
chmod 700 /var/lib/munge /var/log/munge

systemctl enable munge
systemctl start munge

# ------------------------------------------------------------
# Slurm dynamic config
# ------------------------------------------------------------
if ! getent group slurm >/dev/null; then
  groupadd -r slurm
fi
if ! id -u slurm >/dev/null 2>&1; then
  useradd -r -g slurm -d /var/lib/slurm -s /sbin/nologin slurm
fi

mkdir -p /var/spool/slurm /var/spool/slurmd /var/log/slurm /var/lib/slurm /etc/slurm
chown -R slurm:slurm /var/spool/slurm /var/spool/slurmd /var/log/slurm /var/lib/slurm

LOCAL_CPUS="$(nproc)"
SLURM_CONF="/etc/slurm/slurm.conf"

# Header de slurm.conf
cat >"$SLURM_CONF" <<EOF
ClusterName=squidient-aws
ControlMachine=${HEAD_HOSTNAME}

SlurmUser=slurm
SlurmctldPort=6817
SlurmdPort=6818
StateSaveLocation=/var/spool/slurm
SlurmdSpoolDir=/var/spool/slurmd
SlurmctldTimeout=300
SlurmdTimeout=300
SchedulerType=sched/backfill
SelectType=select/cons_tres

EOF

# Lignes NodeName
echo "NodeName=${HEAD_HOSTNAME} CPUs=$LOCAL_CPUS State=UNKNOWN" >>"$SLURM_CONF"
if [ -n "${COMPUTE_NODE_LIST}" ]; then
  for node in ${COMPUTE_NODE_LIST}; do
    echo "NodeName=$node CPUs=$LOCAL_CPUS State=UNKNOWN" >>"$SLURM_CONF"
  done
fi

echo "" >>"$SLURM_CONF"

# Partition debug
PARTITION_NODES="${HEAD_HOSTNAME}"
if [ -n "${COMPUTE_NODE_LIST}" ]; then
  for node in ${COMPUTE_NODE_LIST}; do
    PARTITION_NODES="$PARTITION_NODES,$node"
  done
fi

echo "PartitionName=debug Nodes=$PARTITION_NODES Default=YES MaxTime=INFINITE State=UP" >>"$SLURM_CONF"

chown slurm:slurm "$SLURM_CONF"

# ------------------------------------------------------------
# OpenMPI + alya-mpio-tools (HEAD ONLY)
# ------------------------------------------------------------
if [ "${ROLE}" = "head" ]; then
  OMPI_VERSION="4.1.6"
  OMPI_PREFIX="/shared/openmpi"

  cd /tmp
  wget "https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-$OMPI_VERSION.tar.gz"
  tar -xvf "openmpi-$OMPI_VERSION.tar.gz"
  cd "openmpi-$OMPI_VERSION"

  ./configure --prefix="$OMPI_PREFIX" --enable-mpirun-prefix-by-default
  make -j"$(nproc)"
  make install

  # utiliser cette OpenMPI
  export PATH="$OMPI_PREFIX/bin:$PATH"

  ALYA_MPIO_SRC="/shared/alya-mpio-tools-src"
  ALYA_MPIO_INSTALL="/shared/alya-mpio-tools"

  git clone --depth 1 https://alya.gitlab.bsc.es/alya/alya-mpio-tools.git "$ALYA_MPIO_SRC" || true

  cd "$ALYA_MPIO_SRC"
  mkdir -p build
  cd build

  cmake .. \
    -DCMAKE_C_COMPILER=mpicc \
    -DCMAKE_CXX_COMPILER=mpicxx \
    -DMPIEXEC_PREFLAGS="--allow-run-as-root;--oversubscribe" \
    -DUSE_VTK=OFF \
    -DUSE_SFC=OFF \
    -DCMAKE_INSTALL_PREFIX="$ALYA_MPIO_INSTALL"

  make -j"$(nproc)"
  make install
fi

# ------------------------------------------------------------
# Shared environment for MPI + alya-mpio-tools (ALL NODES)
# ------------------------------------------------------------
cat >/etc/profile.d/shared-hpc-env.sh <<'EOF'
export PATH=/shared/openmpi/bin:/shared/alya-mpio-tools/bin:$PATH
export LD_LIBRARY_PATH=/shared/openmpi/lib:$LD_LIBRARY_PATH
EOF

chmod +x /etc/profile.d/shared-hpc-env.sh

# ------------------------------------------------------------
# Start Slurm daemons
# ------------------------------------------------------------
if [ "${ROLE}" = "head" ]; then
  systemctl enable slurmctld
  systemctl start slurmctld
else
  systemctl disable slurmctld || true
fi

systemctl enable slurmd
systemctl start slurmd

