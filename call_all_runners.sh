for script in /cluster/projects/nn14654k/ylvaos/basis_set_n_funcs/runners/*.sh; do
    bash $script
    rm $script
done

