sed -i 's/{LOCAL_CPUS}/LOCAL_CPUS/g' cloud-init-slurm-fedora.sh
sed -i 's/{node}/node/g' cloud-init-slurm-fedora.sh
sed -i 's/{PARTITION_NODES}/PARTITION_NODES/g' cloud-init-slurm-fedora.sh
sed -i 's/{OMPI_VERSION}/OMPI_VERSION/g' cloud-init-slurm-fedora.sh
