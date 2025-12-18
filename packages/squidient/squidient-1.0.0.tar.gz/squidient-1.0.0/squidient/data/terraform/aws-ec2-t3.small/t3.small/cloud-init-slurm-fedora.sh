#!/bin/bash
set -eux

# --------------------------------------------------------------------
# System update and base packages
# --------------------------------------------------------------------

# Optional but useful to ensure latest security updates (can be slow)
dnf -y update

# Install Slurm, Munge, and build/runtime dependencies
dnf -y install \
  slurm \
  slurm-slurmctld \
  slurm-slurmd \
  munge \
  munge-libs \
  munge-devel \
  cmake \
  gcc \
  gcc-c++ \
  gcc-gfortran \
  git \
  make \
  perl \
  wget \
  python3 \
  python3-pip \
  diffutils \
  which \
  tar \
  gzip \
  bzip2 \
  zlib-devel \
  openssl-devel \
  libibverbs \
  rdma-core \
  numactl \
  numactl-devel \
  environment-modules

# Ensure base system directories are not group-writable (Munge requirement)
chmod 755 /
chmod 755 /var
chmod 755 /var/lib

# --------------------------------------------------------------------
# Munge: authentication service for Slurm
# --------------------------------------------------------------------

# If create-munge-key exists, use it.
# Otherwise, fall back to manual key generation with dd.
if command -v create-munge-key >/dev/null 2>&1; then
  create-munge-key
else
  dd if=/dev/urandom bs=1 count=1024 of=/etc/munge/munge.key
fi

# Correct permissions on the Munge key and directories
chown munge:munge /etc/munge/munge.key
chmod 600 /etc/munge/munge.key

mkdir -p /var/lib/munge /var/log/munge
chown -R munge:munge /etc/munge /var/lib/munge /var/log/munge
chmod 700 /var/lib/munge /var/log/munge

# Enable and start Munge service
systemctl enable munge
systemctl start munge

# --------------------------------------------------------------------
# Slurm: single-node controller + compute daemon
# --------------------------------------------------------------------

# Ensure slurm group exists
if ! getent group slurm >/dev/null 2>&1; then
  groupadd -r slurm
fi

# Ensure slurm user exists
if ! id -u slurm >/dev/null 2>&1; then
  useradd -r -g slurm -d /var/lib/slurm -s /sbin/nologin slurm
fi

# Slurm directories
mkdir -p /var/spool/slurm /var/spool/slurmd /var/log/slurm /var/lib/slurm /etc/slurm
chown -R slurm:slurm /var/spool/slurm /var/spool/slurmd /var/log/slurm /var/lib/slurm

# Hostname for Slurm configuration
HOSTNAME="$(hostname)"

# Minimal single-node slurm.conf
cat >/etc/slurm/slurm.conf <<EOF
ClusterName=squidient-aws
ControlMachine=$HOSTNAME

SlurmUser=slurm
SlurmctldPort=6817
SlurmdPort=6818
StateSaveLocation=/var/spool/slurm
SlurmdSpoolDir=/var/spool/slurmd
SlurmctldTimeout=300
SlurmdTimeout=300
SchedulerType=sched/backfill
SelectType=select/cons_tres

NodeName=${HOSTNAME} CPUs=$(nproc) State=UNKNOWN
PartitionName=debug Nodes=${HOSTNAME} Default=YES MaxTime=INFINITE State=UP
EOF

chown slurm:slurm /etc/slurm/slurm.conf

# Enable and start Slurm services (controller + daemon)
# The unit files should exist thanks to slurm-slurmctld / slurm-slurmd packages.
systemctl enable slurmctld
systemctl enable slurmd
systemctl start slurmctld
systemctl start slurmd

# --------------------------------------------------------------------
# OpenMPI 4.x: build and install from source
# --------------------------------------------------------------------

OMPI_VERSION="4.1.6"
cd /tmp
wget https://download.open-mpi.org/release/open-mpi/v4.1/openmpi-$OMPI_VERSION.tar.gz
tar -xvf openmpi-$OMPI_VERSION.tar.gz
cd openmpi-$OMPI_VERSION

./configure --prefix=/opt/openmpi --enable-mpirun-prefix-by-default
make -j"$(nproc)"
make install

# Make OpenMPI available for all users
echo 'export PATH=/opt/openmpi/bin:$PATH' >> /etc/profile.d/openmpi.sh
echo 'export LD_LIBRARY_PATH=/opt/openmpi/lib:$LD_LIBRARY_PATH' >> /etc/profile.d/openmpi.sh
chmod +x /etc/profile.d/openmpi.sh

# --------------------------------------------------------------------
# Alya MPIO tools: build & install from Git
# --------------------------------------------------------------------

# Ensure we use the OpenMPI we just installed
export PATH=/opt/openmpi/bin:$PATH

# Source and install directories
ALYA_MPIO_SRC=/opt/alya-mpio-tools-src
ALYA_MPIO_INSTALL=/opt/alya-mpio-tools

# Clone sources (BSC internal Git)
git clone --depth 1 https://alya.gitlab.bsc.es/alya/alya-mpio-tools.git "$ALYA_MPIO_SRC"

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

# Expose alya-mpio-tools to all users
echo "export PATH=$ALYA_MPIO_INSTALL/bin:\$PATH" > /etc/profile.d/alya-mpio-tools.sh
chmod +x /etc/profile.d/alya-mpio-tools.sh

