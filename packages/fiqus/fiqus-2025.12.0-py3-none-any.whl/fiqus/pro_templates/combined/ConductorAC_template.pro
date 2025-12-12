Group {
    // ------- PROBLEM DEFINITION -------
    // Filaments
    Filaments_SC = Region[{<<rm.powered.Filaments.vol.numbers|join(', ')>>}]; // Filament superconducting region
    Filament_holes = Region[{<<rm.powered.Filaments.surf_in.numbers|join(', ')>>}]; // Filament holes

    // Filaments = Region[{Filaments_SC, Filament_holes}]; // Filaments (including holes) - not used

    BndFilaments = Region[{<<rm.powered.Filaments.surf.numbers|join(', ')>>}]; // Filament boundaries
    BndFilaments_holes = Region[{<<rm.insulator.curve.numbers|join(', ')>>}]; // Filament hole boundaries
    Cuts = Region[{<<rm.powered.Filaments.cochain.numbers|join(', ')>>}]; // Cuts on filament boundaries

    // Define the filaments, boundaries and cuts according to their layer and index in the layer
    {% if len(rm.powered.Filaments.vol.numbers) % 6 == 0 %} // There is no inner layer (of length 1)
        {% for layer in range( int(len(rm.powered.Filaments.vol.numbers)/6 )) %}
            {% for filament_index in range(6) %}
                filament_<<layer + 1>>_<<filament_index + 1>> = Region[{<<rm.powered.Filaments.vol.numbers[layer*6 + filament_index]>>}]; // Filament surface
                filamentBnd_<<layer + 1>>_<<filament_index + 1>> = Region[{<<rm.powered.Filaments.surf.numbers[layer*6 + filament_index]>>}]; // Boundary
                Cut_<<layer + 1>>_<<filament_index + 1>> = Region[{<<rm.powered.Filaments.cochain.numbers[layer*6 + filament_index]>>}]; // Cut
            {%endfor%}
        {%endfor%}

    {% elif len(rm.powered.Filaments.vol.numbers) % 6 == 1 %} // There is an inner layer (of length 1)
        // Define the inner point
        filament_0_0 = Region[{<<rm.powered.Filaments.vol.numbers[0]>>}];
        filamentBnd_0_0 = Region[{<<rm.powered.Filaments.surf.numbers[0]>>}];
        Cut_0_0 = Region[{<<rm.powered.Filaments.cochain.numbers[0]>>}];

        {% for layer in range(0, int((len(rm.powered.Filaments.vol.numbers)-1) /6 ) ) %}
            {% for filament_index in range(6) %}
                filament_<<layer + 1>>_<<filament_index + 1>> = Region[{<<rm.powered.Filaments.vol.numbers[layer*6 + filament_index + 1]>>}];
                filamentBnd_<<layer + 1>>_<<filament_index + 1>> = Region[{<<rm.powered.Filaments.surf.numbers[layer*6 + filament_index + 1]>>}];
                Cut_<<layer + 1>>_<<filament_index + 1>> = Region[{<<rm.powered.Filaments.cochain.numbers[layer*6 + filament_index + 1]>>}];
            {%endfor%}
        {%endfor%}

    {% endif %}

    // To assign different material properties to each filament hole, we need to assign them separately.
    {% for i, hole in enumerate(rm.powered.Filaments.surf_in.numbers) %}
        FilamentHole_<<i>> = Region[{<<hole>>}];
    {%endfor%}

    // Matrix partitions
    {% for i, matrix_partition in enumerate(rm.induced.Matrix.vol.numbers)%}
        Matrix_<<i>> = Region[{<<matrix_partition>>}];
    {%endfor%}

    // Matrix
    Matrix = Region[{<<rm.induced.Matrix.vol.numbers|join(', ')>>}];
    BndMatrix = Region[ <<rm.induced.Matrix.surf_out.numbers[0]>> ]; // Strand outer boundary
    BndMatrixCut = Region[ {<<rm.induced.Matrix.cochain.numbers|join(', ')>>} ]; // Strand outer boundary cut

    // Air
    Air = Region[<<rm.air.vol.number>>]; // Air surface
    BndAir = Region[<<rm.air.surf.number>>]; // Air outer boundary

    // Cuts
    {% if dm.magnet.geometry.type == 'periodic_square' %}
        // Manual cuts
        CutAirVertical = Region[<<rm.air.cochain.numbers[0]>>];
        AirVerticalBoundary = Region[<<rm.air.cochain.numbers[1]>>];
        CutAirHorizontal = Region[<<rm.air.cochain.numbers[2]>>];
        AirHorizontalBoundary = Region[<<rm.air.cochain.numbers[3]>>];

        BndMatrixCut += Region[{CutAirVertical, CutAirHorizontal}];
        // Transition Layers of cuts
        CutAirVerticalTL = ElementsOf[AirVerticalBoundary, OnOneSideOf CutAirVertical];
        CutAirHorizontalTL = ElementsOf[AirHorizontalBoundary, OnOneSideOf CutAirHorizontal];

        // Domain boundaries for periodic condition
        BndDomainTop = Region[<<rm.induced.Domain.surf_out.numbers[0]>>];
        BndDomainBottom = Region[<<rm.induced.Domain.surf_out.numbers[1]>>];
        BndDomainLeft = Region[<<rm.induced.Domain.surf_out.numbers[2]>>];
        BndDomainRight = Region[<<rm.induced.Domain.surf_out.numbers[3]>>];
    {% endif %}
    // Cuts +=  Region[BndMatrixCut]; // The matrix cut is not part of the 'Cuts' group anymore, but is rtreated separately

    // Define a region for the matrix partitions to be included in the TI (transverse currents) problem
    TI_adjacent_region = Region[ {Air} ]; // Define the regions adjacent to the region on which the TI problem is solved (used for defining h_perp_space_dynamic)
    {% if dm.magnet.geometry.io_settings.load.load_from_yaml %}
    Matrix_partitions_excluded_from_TI = Region[{<<mp.Surfaces_excluded_from_TI|join(', ')>>}]; // Matrix partitions excluded from the TI problem

    Matrix_partitions_for_TI = Region[ {Matrix} ];
    Matrix_partitions_for_TI -= Region[ {Matrix_partitions_excluded_from_TI} ]; // Matrix partitions included in the TI problem

    TI_adjacent_region += Region[ {Matrix_partitions_excluded_from_TI} ]; // Define the regions adjacent to the region on which the TI problem is solved (used for defining h_perp_space_dynamic)
    {% else %}
    Matrix_partitions_for_TI = Region[ {Matrix} ];
    {% endif %}

    {% if dm.magnet.solve.diffusion_barriers.enable %}
    // Regions for resistors representing diffusion barriers
    Resistors_diffusion_barrier = Region[ {} ]; // Initialize the region for the resistors representing diffusion barriers
    {% if len(rm.powered.Filaments.vol.numbers) % 6 == 0 %} // There is no inner layer (of length 1)
        {% for layer in range( int(len(rm.powered.Filaments.vol.numbers)/6 )) %}
            {% for filament_index in range(6) %}
                R_diffusion_barrier_<<layer+1>>_<<filament_index+1>> = Region[{<<5000 + layer*6 + filament_index + 1>>}];
                Resistors_diffusion_barrier += Region[{R_diffusion_barrier_<<layer+1>>_<<filament_index+1>>}];
            {%endfor%}
        {%endfor%}

    {% elif len(rm.powered.Filaments.vol.numbers) % 6 == 1 %} // There is an inner layer (of length 1)

        {% for layer in range(0, int((len(rm.powered.Filaments.vol.numbers)-1) /6 ) ) %}
            {% for filament_index in range(6) %}
                R_diffusion_barrier_<<layer+1>>_<<filament_index+1>> = Region[{<<5000 + layer*6 + filament_index + 1>>}];
                Resistors_diffusion_barrier += Region[{R_diffusion_barrier_<<layer+1>>_<<filament_index+1>>}];
            {%endfor%}
        {%endfor%}

    {% endif %}
    {% endif %}

    {% if dm.magnet.solve.global_diffusion_barrier.enable %}
    // Defining physical regions for the global diffusion barrier in the matrix between filament region and external region
    GlobalDiffusionBarrier = Region[ {<<mp.GlobalDiffusionBarrier.RegionTag>>} ]; // the barrier itself
    MatrixInternalSurface = Region[ {<<mp.GlobalDiffusionBarrier.InternalRegionTag>>} ]; // the physical region inside of it, of which the barrier is the external boundary
                                                                                         //  (for safe implementation of the discontinuous function space, instead of OnOneSideOf, which depends on the orientation of the curves)
    {% endif %}

    // Split into conducting and non-conducting domains
    {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes == 'None' or dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes == 0.0 %}
    // Holes are treated as air -> non-conducting domain
    LinOmegaC = Region[ {Matrix} ];
    BndOmegaC = Region[ {BndMatrix, BndFilaments, BndFilaments_holes} ];
    OmegaCC = Region[ {Air, Filament_holes} ];
    {% else %}
    // Holes are conducting -> part of the conducting domain
    LinOmegaC = Region[ {Matrix, Filament_holes} ];
    BndOmegaC = Region[ {BndMatrix, BndFilaments} ];
    OmegaCC = Region[ {Air} ];
    {% endif %}
    NonLinOmegaC = Region[ {Filaments_SC} ];
    OmegaC = Region[ {LinOmegaC, NonLinOmegaC} ];
    Omega = Region[ {OmegaC, OmegaCC} ]; // the whole domain (only surfaces in 2D, or volumes in 3D)

    OmegaC_AndBnd = Region[{OmegaC, BndOmegaC}]; // useful for function space definition
    OmegaCC_AndBnd = Region[{OmegaCC, BndOmegaC, BndAir}]; // useful for function space definition

    // Here we define points on the boundaries of the filaments and the outer matrix boundary.
    // These points are used to fix the magnetic potential to zero on the boundaries.
    MatrixPointOnBoundary = Region[<<rm.air.point.numbers[0]>>];
    FilamentPointsOnBoundaries = Region[{<<rm.powered.Filaments.curve.numbers|join(', ')>>}];
    ArbitraryPoints = Region[{MatrixPointOnBoundary, FilamentPointsOnBoundaries}];

}

Function{
    // ------- GEOMETRY PARAMETERS -------
    {% if len(rm.powered.Filaments.vol.numbers) % 6 == 0 %}
        number_of_layers = <<len(rm.powered.Filaments.vol.numbers)>>/6;
    {% elif len(rm.powered.Filaments.vol.numbers) % 6 == 1 %}
        number_of_layers = (<<len(rm.powered.Filaments.vol.numbers)>>-1) / 6;
    {% endif %}

    // Set correction factor based on the periodicity length
    {% if dm.magnet.solve.formulation_parameters.two_ell_periodicity %}
        correctionFactor = 0.827; // to be automatized (equal to sin(x)/x with x = pi*ell/p, with ell = p/6 in the hexagonal lattice case)
        ell = 2*correctionFactor * <<dm.conductors[dm.magnet.solve.conductor_name].strand.fil_twist_pitch>> / 6;
    {% else %}
        correctionFactor = 0.9549;
        ell = correctionFactor * <<dm.conductors[dm.magnet.solve.conductor_name].strand.fil_twist_pitch>> / 6;
    {% endif %}

    // ------- MATERIAL PARAMETERS -------
    temperature = <<dm.magnet.solve.general_parameters.temperature>>;
    T[] = temperature; // this can be made a function of time if needed. Later on, T may also be a field we solve for.


    mu0 = Pi*4e-7; // [H/m]
    nu0 = 1.0/mu0; // [m/H]
    mu[Omega] = mu0;
    nu[Omega] = nu0;


    // Assigning resistances associated with diffusion barriers:
    {% if dm.magnet.solve.diffusion_barriers.enable %}
        {% if dm.magnet.geometry.io_settings.load.load_from_yaml and dm.magnet.solve.diffusion_barriers.load_data_from_yaml %}
            // If we load the geometry from a YAML file, we can load the resistances of the diffusion barriers from the YAML file.
            {% for layer in range( int(len(rm.powered.Filaments.vol.numbers)/6 )) %}
                {% for filament_index in range(6) %}
    R[R_diffusion_barrier_<<layer+1>>_<<filament_index+1>>] = <<mp.DiffusionBarriers.FilamentResistances[layer*6 + filament_index]>>; // [Ohm]
                {% endfor %}
            {% endfor %}
        {% else %}
            // If we don't load the geometry from a YAML file, we can assign the resistances of the diffusion barriers from the material properties data structure.
            {% for layer in range( int(len(rm.powered.Filaments.vol.numbers)/6 )) %}
                {% for filament_index in range(6) %}
    R[R_diffusion_barrier_<<layer+1>>_<<filament_index+1>>] = <<mp.DiffusionBarriers.FilamentResistances[layer*6 + filament_index]>>; // [Ohm]
                {% endfor %}
            {% endfor %}
        {% endif %}
    {% endif %}

    {% if dm.magnet.solve.global_diffusion_barrier.enable %}
    // Handling global diffusion barrier in the matrix between filament region and external region
    rho_contact[GlobalDiffusionBarrier] = <<mp.GlobalDiffusionBarrier.ContactResistivity>>;
    {% endif %}

    // Copper-like Matrix
    {% if isinstance(dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer, float) %} // If the matrix has constant resistivity we can assign it directly
        rho[Matrix] = <<dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer>>;
    {% elif dm.magnet.geometry.io_settings.load.load_from_yaml %}
        // If we load the geometry from a YAML file, we also have material properties assigned in a MaterialProperties (mp) data structure.
        // This is a temporary solution. It reads the material property functions from the input YAML file and only assigns the RRR value from the geometry YAML.
        // In the future the material properties should be assigned directly from the geometry YAML.
        {% for i, matrix_partition_material in zip(range(len(rm.induced.Matrix.vol.numbers)), rm.induced.Matrix.vol.names)%}
            {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer == 'CFUN_rhoCu_T' %}
                rho[Matrix_<<i>>] = CFUN_rhoCu_T[T[]]{0, << mp.Materials[matrix_partition_material].RRR >>};
            {% elif dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer == 'CFUN_rhoCu' %}
                rho[Matrix_<<i>>] = CFUN_rhoCu_T_B[T[], $1]{<< mp.Materials[matrix_partition_material].RRR >>};
            {% endif %}
        {%endfor%}
    {% elif dm.conductors[dm.magnet.solve.conductor_name].strand.RRR is iterable %}
        {% for i, RRR_i in enumerate(dm.conductors[dm.magnet.solve.conductor_name].strand.RRR) %}
            {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer == 'CFUN_rhoCu_T' %}
                rho[Matrix_<<i>>] = CFUN_rhoCu_T[T[]]{0, <<RRR_i>>};
            {% elif dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer == 'CFUN_rhoCu' %}
                rho[Matrix_<<i>>] = CFUN_rhoCu_T_B[T[], $1]{<<RRR_i>>};
            {% endif %}
        {%endfor%}
    {% else %} // If we don't load the geometry from a YAML file, we can assign the material properties directly
        RRR_matrix = <<dm.conductors[dm.magnet.solve.conductor_name].strand.RRR>>;
        {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer == 'CFUN_rhoCu_T' %}
            rho[Matrix] = CFUN_rhoCu_T[T[]]{0, RRR_matrix};
        {% elif dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_stabilizer == 'CFUN_rhoCu' %}
            rho[Matrix] = CFUN_rhoCu_T_B[T[], $1]{RRR_matrix}; //1.81e-10; //
            // rho[Matrix_0] = CFUN_rhoCu_T_B[T[], $1]{10}; //1.81e-10; //
            // rho[Matrix_1] = CFUN_rhoCu_T_B[T[], $1]{100}; //1.81e-10; //
            // rho[Matrix_2] = CFUN_rhoCu_T_B[T[], $1]{1000}; //1.81e-10; //
        {% endif %}
    {% endif %}

    // Superconducting filaments (nonlinear now)
    ec = <<dm.conductors[dm.magnet.solve.conductor_name].strand.ec_superconductor>>; // [V/m], the value 1e-4 V/m is a common convention

    {% if dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Ic_A_NbTi' and dm.conductors[dm.magnet.solve.conductor_name].strand.material_superconductor == 'NbTi' %}
        jc[] = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Jc_5T_4_2K>> / 1.70732393e9 * CFUN_IcNbTi_T_B_a[T[], $1, 1]; // [A/m2] critical current density as function of temperature and field amplitude
    {% elif dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Ic_A_Nb3Sn' and dm.conductors[dm.magnet.solve.conductor_name].strand.material_superconductor == 'Nb3Sn' %}
        jc[] = CFUN_IcNb3Sn_T_B_a[T[], $1, 1]; // [A/m2] critical current density as function of temperature and field amplitude
    {% elif dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Bottura' and dm.conductors[dm.magnet.solve.conductor_name].strand.material_superconductor == 'Nb3Sn' %}
        Tc0_Bottura = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Tc0_Bottura>>;
        Bc20_Bottura = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Bc20_Bottura>>;
        C0_Bottura = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.C0_Bottura>>;
        jc[] = CFUN_Jc_Nb3Sn_Bottura_T_B[T[], $1]{Tc0_Bottura, Bc20_Bottura, C0_Bottura, 0.5, 2, 1, 1}; // p = 0.5, q = 2
    {% elif dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Bordini' %}
        C0_Bordini = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.C0_Bordini>>;
        Tc0_Bordini = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Tc0_Bordini>>;
        Bc20_Bordini = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Bc20_Bordini>>;
        alpha_Bordini = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.alpha_Bordini>>;
        jc[] = CFUN_Jc_Bordini_T_B[T[], $1]{C0_Bordini, Tc0_Bordini, Bc20_Bordini, alpha_Bordini};
    {% elif dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Nb3Sn_HFM' %}
        C0_Nb3Sn_HFM = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.C0_Nb3Sn_HFM>>;
        Tc0_Nb3Sn_HFM = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Tc0_Nb3Sn_HFM>>;
        Bc20_Nb3Sn_HFM = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Bc20_Nb3Sn_HFM>>;
        alpha_Nb3Sn_HFM = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.alpha_Nb3Sn_HFM>>;
        nu_Nb3Sn_HFM = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.nu_Nb3Sn_HFM>>;
        p_Nb3Sn_HFM = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.p_Nb3Sn_HFM>>;
        q_Nb3Sn_HFM = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.q_Nb3Sn_HFM>>;
        jc[] = CFUN_Jc_Nb3Sn_HFM_T_B[T[], $1]{C0_Nb3Sn_HFM, Tc0_Nb3Sn_HFM, Bc20_Nb3Sn_HFM, alpha_Nb3Sn_HFM, nu_Nb3Sn_HFM, p_Nb3Sn_HFM, q_Nb3Sn_HFM};
    {% elif dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'ProDefined' %}
        C0 = <<float(dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.C0)>>;
        Tc0 = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Tc0>>;
        Bc20 = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Bc20>> + <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.B0>>;
        alpha = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.alpha>>;
        p = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.p>>;
        q = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.q>>;
        v = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.v>>;
        B0 = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.B0>>;
        jc[] = (C0 * (1 - (T[] / Tc0)^v)^alpha * (1 - (T[] / Tc0)^2)^alpha) / (Abs[$1] + B0) * (Min[(Abs[$1] + B0) / (Bc20 * (1 - (T[] / Tc0)^v)), 1])^p * (1 - Min[(Abs[$1] + B0) / (Bc20 * (1 - (T[] / Tc0)^v)), 1])^q ;

    {% elif dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type == 'Constant Jc' %}
        jc[] = <<dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.Jc_constant>>; // [A/m2] constant critical current density
    {% endif %}

    // Power law
    eps_jc[] = <<dm.conductors[dm.magnet.solve.conductor_name].strand.minimum_jc_fraction>> * jc[<<dm.conductors[dm.magnet.solve.conductor_name].strand.minimum_jc_field>>];
    n = <<dm.conductors[dm.magnet.solve.conductor_name].strand.n_value_superconductor>>; // [-] power law index, one key parameter for the power law
    rho_power[] = ec / (Max[jc[$2],eps_jc[]]) * (Norm[$1] / (Max[jc[$2],eps_jc[]]))^(n - 1); // [Ohm m] power law resistivity
    e_power[] = rho_power[$1, $2] * $1;
    dedj_power[] = (
        ec / ((Max[jc[$2],eps_jc[]])#1) * (Norm[$1]/#1)^(n - 1) * TensorDiag[1, 1, 1] +
        ec / (#1)^3 * (n - 1) * (Norm[$1]/#1)^(n - 3) * SquDyadicProduct[$1]);

    db = 0.005;
    // outer_product[] = Tensor[CompX[$1]*CompX[$2], CompX[$1]*CompY[$2], CompX[$1]*CompZ[$2], CompY[$1]*CompX[$2], CompY[$1]*CompY[$2], CompY[$1]*CompZ[$2], CompZ[$1]*CompX[$2], CompZ[$1]*CompY[$2], CompZ[$1]*CompZ[$2]];
    // dedb_power[] = -n*ec/jc[Norm[$2]]^2 * (Norm[$1]/jc[Norm[$2]])^(n-1) * ( jc[Norm[$2] + db] - jc[Max[0, Norm[$2] - db]] ) / (2*db) * outer_product[$1, $2]/(Norm[$2]+1e-10); // Is this one correct?
    dedb_power[] = Tensor[  CompX[(e_power[$1, Norm[$2+Vector[db,0,0]]] - e_power[$1, Norm[$2+Vector[-db,0,0]]])#1],
                            CompX[(e_power[$1, Norm[$2+Vector[0,db,0]]] - e_power[$1, Norm[$2+Vector[0,-db,0]]])#2],
                            CompX[(e_power[$1, Norm[$2+Vector[0,0,db]]] - e_power[$1, Norm[$2+Vector[0,0,-db]]])#3],
                        CompY[#1], CompY[#2], CompY[#3],
                        CompZ[#1], CompZ[#2], CompZ[#3]] / (2*db);

    // Trials for extending the power to overcritical regimes
    rho_N = 1e-7; // Resistivity of the filaments in their normal state
    // 1) This first option shows very poor convergence properties: fails to convergence at the transition from normal state to superconducting state (NaN)
    // rho_power_normal[] = Min[rho_power[$1, $2], rho_N];
    // dedj_power_normal[] = (rho_power[$1, $2] <= rho_N) ? dedj_power[$1, $2] : rho_N * TensorDiag[1, 1, 1];
    // dedb_power_normal[] = (jc[Norm[$2]] > eps_jc) ? dedb_power[$1, $2] : TensorDiag[0, 0, 0];
    // 2) The second option below also shows very poor convergence: iteration cycles
    // rho_power_normal[] = 1. / (1./rho_power[$1,$2] + 1./rho_N);
    rho_power_normal[] = rho_power[$1,$2] / (1 + rho_power[$1,$2]/rho_N);
    dedj_power_normal[] = rho_power_normal[$1,$2] * TensorDiag[1, 1, 1] + ec*(n-1)*Norm[$1]^(n-3) /((Max[jc[$2],eps_jc[]])^n)/(1+rho_power[$1,$2]/rho_N)^2 * SquDyadicProduct[$1];
    // dedb_power_normal[] = 1./(1+rho_power[$1,Norm[$2]]/rho_N)^2 * dedb_power[$1,$2];
    // 3) Third option with log-sum-exp expression to describe the transition... to be tried.


    {% if dm.magnet.solve.general_parameters.superconductor_linear %}
    mult_copper_like = 1e-5;
    // Set everything to copper
    rho[Filaments_SC] = 1.81e-10;
    dedj[Filaments_SC] = 1.81e-10;
    {% else %}
    rho[Filaments_SC] = rho_power[$1, $2];
    dedj[Filaments_SC] = dedj_power[$1, $2];
    // rho[Filaments_SC] = rho_power_normal[$1, $2]; // Power law in parallel with constant resistivity -> poor convergence is observed
    // dedj[Filaments_SC] = dedj_power_normal[$1, $2];
    {% endif %}
    // The de/db Jacobian is not used for the moment
    dedb[Filaments_SC] = dedb_power[$1, $2];
    // dedb[Filaments_SC] = dedb_power_normal[$1, $2]; // Poor convergence observed (cycles)

    {% if dm.magnet.geometry.io_settings.load.load_from_yaml %}
        // We assign material properties to each filament hole. Currently we just assign the same properties as the matrix, but with a different RRR.
        // This must be updated to actually use the correct material property read from the geometry YAML.
        {% for i, hole_material in zip(range(len(rm.powered.Filaments.surf_in.numbers)), rm.powered.Filaments.surf_in.names)%}
            {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes == 'CFUN_rhoCu_T' %}
                rho[FilamentHole_<<i>>] = CFUN_rhoCu_T[T[]]{0, << mp.Materials[hole_material].RRR >>};
            {% elif dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes == 'CFUN_rhoCu_T_B' %}
                rho[FilamentHole_<<i>>] = CFUN_rhoCu_T_B[T[], $1]{<< mp.Materials[hole_material].RRR >>};
            {% elif isinstance(dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes, float) %} // If the matrix has constant resistivity we can assign it directly
                {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes %} // non-zero
                    rho[FilamentHole_<<i>>] = <<dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes>>;
                {% endif %}
            {% endif %}
        {% endfor %}
    {% else %} // parametric geometry
        {% if dm.conductors[dm.magnet.solve.conductor_name].strand.filament_hole_diameter %} // only if holes are present
            {% for i, hole_material in zip(range(len(rm.powered.Filaments.surf_in.numbers)), rm.powered.Filaments.surf_in.names)%}
                {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes == 'CFUN_rhoCu_T' %}
                    rho[FilamentHole_<<i>>] = CFUN_rhoCu_T[T[]]{0, 50};   // only temporary as the hole material should be air
                {% elif dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes == 'CFUN_rhoCu_T_B' %}
                    rho[FilamentHole_<<i>>] = CFUN_rhoCu_T_B[T[], $1]{50};  // only temporary as the hole material should be air
                {% elif isinstance(dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes, float) %} // If the matrix has constant resistivity we can assign it directly
                    {% if dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes %} // non-zero
                        rho[FilamentHole_<<i>>] = <<dm.conductors[dm.magnet.solve.conductor_name].strand.rho_material_holes>>;
                    {% endif %}
                {% endif %}
            {% endfor %}
        {% endif %}
    {% endif %}

    sigma[] = 1/rho[$1] ; // Can only be used in the matrix

    // HEAT APPROXIMATION
    {% if dm.conductors[dm.magnet.solve.conductor_name].strand.Cv_material_superconductor == 'CFUN_CvNbTi' %}
        filament_Cv[] = CFUN_CvNbTi_T_B[$1, $2]{0, 1, 0}; // Volumetric heat capacity [J/(m3 K)], as function of temperature and field magnitude.
    {% elif dm.conductors[dm.magnet.solve.conductor_name].strand.Cv_material_superconductor == 'CFUN_CvNb3Sn' %}
        filament_Cv[] = CFUN_CvNb3Sn_T_B[$1, $2]; // Volumetric heat capacity [J/(m3 K)], as function of temperature and field magnitude.
    {% endif %}

    {% if dm.conductors[dm.magnet.solve.conductor_name].strand.Cv_material_stabilizer == 'CFUN_CvCu' %}
        matrix_Cv[] = CFUN_CvCu_T[$1]; // Volumetric heat capacity [J/(m3 K)], as function of temperature
    {% endif %}

    // ------- SOURCE PARAMETERS -------
    directionApplied[] = Vector[Cos[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], Sin[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], 0.];
    // same for piecewise and sine
    {% if dm.magnet.solve.source_parameters.source_type == 'sine' %}
        // Sine wave source (with DC component)
        f = <<dm.magnet.solve.source_parameters.sine.frequency>>; // Frequency of applied field [Hz]

        time_multiplier = 1; // Set to 1, as it is being used in the resolution

        // ramp_duration = -5e-2 / f; // Ramp duration for constant source components
        // quad_ramp_I[] = (Sqrt[<<dm.magnet.solve.source_parameters.sine.superimposed_DC.current_magnitude>>] / ramp_duration * $Time )^2;
        // constant_I_transport[] = ($Time < ramp_duration ) ? InterpolationLinear[$Time]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.sine.superimposed_DC.current_magnitude>>}]}  : <<dm.magnet.solve.source_parameters.sine.superimposed_DC.current_magnitude>>;
        constant_I_transport[] = <<dm.magnet.solve.source_parameters.sine.superimposed_DC.current_magnitude>>;
        I_transport[] =  constant_I_transport[$Time] + <<dm.magnet.solve.source_parameters.sine.current_amplitude>> * Sin[2*Pi*f * $Time];

        constant_field_magnitude = <<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>;
        hsVal[] = nu0 * (<<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * $Time] + constant_field_magnitude) * directionApplied[];
        hsVal_prev[] = nu0 *(<<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * ($Time-$DTime)] + constant_field_magnitude) * directionApplied[];

    {% elif dm.magnet.solve.source_parameters.source_type == 'rotating' %}
        // Rotating magnetic field
        f = <<dm.magnet.solve.source_parameters.rotating.frequency>>;
        ramp_duration = 1e-1  / f;

        time_multiplier = 1;
        I_transport[] = 0;
        constant_field_magnitude[] = ($Time < ramp_duration ) ? InterpolationLinear[$Time]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.rotating.field_magnitude>>}]} : <<dm.magnet.solve.source_parameters.rotating.field_magnitude>>;
        constant_field_magnitude_prev[] = ($Time-$DTime < ramp_duration ) ? InterpolationLinear[$Time-$DTime]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.rotating.field_magnitude>>}]} : <<dm.magnet.solve.source_parameters.rotating.field_magnitude>>;

        hsVal[] = nu0 * constant_field_magnitude[] * Vector[Cos[2*Pi*f*$Time], Sin[2*Pi*f*$Time], 0.];
        hsVal_prev[] = nu0 * constant_field_magnitude_prev[] * Vector[Cos[2*Pi*f*($Time-$DTime)], Sin[2*Pi*f*($Time-$DTime)], 0.];

    {% elif dm.magnet.solve.source_parameters.source_type == 'piecewise' %}

        time_multiplier = <<dm.magnet.solve.source_parameters.piecewise.time_multiplier>>;
        applied_field_multiplier = <<dm.magnet.solve.source_parameters.piecewise.applied_field_multiplier>>;
        transport_current_multiplier = <<dm.magnet.solve.source_parameters.piecewise.transport_current_multiplier>>;

        {% if dm.magnet.solve.source_parameters.piecewise.source_csv_file %} // Source from CSV file
            timeList() = {<<ed['time']|join(', ')>>};
            valueList() = {<<ed['value']|join(', ')>>};
            timeValuesList() = ListAlt[timeList(), valueList()];

            hsVal[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{List[timeValuesList()]} * directionApplied[];
            hsVal_prev[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time-$DTime)/time_multiplier]]{List[timeValuesList()]} * directionApplied[];
            I_transport[] = transport_current_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{List[timeValuesList()]};

        {% else %} // Source from parameters
            times_source_piecewise_linear() = {<<dm.magnet.solve.source_parameters.piecewise.times|join(', ')>>};
            transport_currents_relative_piecewise_linear() = {<<dm.magnet.solve.source_parameters.piecewise.transport_currents_relative|join(', ')>>};
            applied_fields_relative_piecewise_linear() = {<<dm.magnet.solve.source_parameters.piecewise.applied_fields_relative|join(', ')>>};

            hsVal[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{ListAlt[times_source_piecewise_linear(), applied_fields_relative_piecewise_linear()]} * directionApplied[];
            hsVal_prev[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time-$DTime)/time_multiplier]]{ListAlt[times_source_piecewise_linear(), applied_fields_relative_piecewise_linear()]} * directionApplied[];
            I_transport[] = transport_current_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{ListAlt[times_source_piecewise_linear(), transport_currents_relative_piecewise_linear()]};
        {% endif %}
    {% endif %}

    // For the natural boundary condition (restricted to fields of constant direction for the moment, should be generalized)
    dbsdt[] = mu0 * (hsVal[] - hsVal_prev[]) / $DTime; // must be a finite difference to avoid error accumulation

    // ------- NUMERICAL PARAMETERS -------
    timeStart = 0.; // Initial time [s]

    {% if dm.magnet.solve.source_parameters.source_type == 'sine'%}
        timeFinal = <<dm.magnet.solve.numerical_parameters.sine.number_of_periods_to_simulate>>/f; // Final time for source definition (s)
        dt = 1 / (f*<<dm.magnet.solve.numerical_parameters.sine.timesteps_per_period>>); // Time step (initial if adaptive) (s)
        dt_max = dt; // Fixed maximum time step
        dt_max_var[] = dt_max;
    {% elif dm.magnet.solve.source_parameters.source_type == 'rotating'%}
        timeFinal = <<dm.magnet.solve.numerical_parameters.rotating.number_of_periods_to_simulate>>/f; // Final time for source definition (s)
        dt = 1 / (f*<<dm.magnet.solve.numerical_parameters.rotating.timesteps_per_period>>); // Time step (initial if adaptive) (s)
        dt_max = dt; // Fixed maximum time step
        dt_max_var[] = dt_max;
    {% else %}
        timeFinal = <<dm.magnet.solve.numerical_parameters.piecewise.time_to_simulate>>;

        {% if dm.magnet.solve.numerical_parameters.piecewise.variable_max_timestep %}
            times_max_timestep_piecewise_linear() = {<<dm.magnet.solve.numerical_parameters.piecewise.times_max_timestep_piecewise_linear|join(', ')>>};
            max_timestep_piecewise_linear() = {<<dm.magnet.solve.numerical_parameters.piecewise.max_timestep_piecewise_linear|join(', ')>>};
            dt = max_timestep_piecewise_linear(0);
            dt_max_var[] = InterpolationLinear[Max[0,$Time]]{ListAlt[times_max_timestep_piecewise_linear(), max_timestep_piecewise_linear()]};
        {% else %}
            dt = timeFinal / <<dm.magnet.solve.numerical_parameters.piecewise.timesteps_per_time_to_simulate>>;
            dt_max = dt; // Fixed maximum time step
            dt_max_var[] = dt_max;
        {% endif %}

        {% if dm.magnet.solve.numerical_parameters.piecewise.force_stepping_at_times_piecewise_linear%}
            control_time_instants_list() = {<<dm.magnet.solve.source_parameters.piecewise.times|join(', ')>>, 1e99}; // last one is just to avoid 'seg. fault' errors
        {% endif %}

    {% endif %}



    iter_max = 60; // Maximum number of iterations (after which we exit the iterative loop)
    extrapolationOrder = 1; // Extrapolation order for predictor
    tol_energy = 1e-6; // Tolerance on the relative change of the power indicator
    writeInterval = dt; // Time interval to save the solution [s]

    // ------- SIMULATION NAME -------
    name = "text_output";
    resDirectory = StrCat["./",name];
    infoResidualFile = StrCat[resDirectory,"/residual.txt"];
    outputPower = StrCat[resDirectory,"/power.txt"]; // File updated during runtime
    crashReportFile = StrCat[resDirectory,"/crash_report.txt"];
    outputTemperature = StrCat[resDirectory,"/temperature.txt"];

    {% if dm.magnet.solve.initial_conditions.init_type == 'pos_file' %}
    h_from_file[] = VectorField[XYZ[]]; // After GmshRead[] in Resolution, this vector field contains the solution from a .pos file that can be accessed at any point XYZ[]
    {% endif %}
}

Constraint {
    { Name phi ;
        Case {
            // For natural boundary condition (in formulation)  if dm.magnet.geometry.type == 'strand_only'
            {Region ArbitraryPoints ; Value 0.0 ;} // Fix the magnetic potential to zero on the boundaries of the filaments and the outer matrix boundary
            //{Region BndAir ; Type Assign ; Value XYZ[]*directionApplied[] ; TimeFunction hsVal[] * directionApplied[] ;} // Essential boundary condition (not compatible with transport current)
            {% if dm.magnet.geometry.type == 'periodic_square' %}
            // Link phi top to bottom
            {
                Region BndDomainBottom ;
                Type Link ;
                RegionRef BndDomainTop ;
                Coefficient 1.0 ;
                Function Vector[X[], Y[] + <<dm.magnet.geometry.air_radius*2>>, Z[]] ;
            }
            // Link phi left to right
            {
                Region BndDomainLeft ;
                Type Link ;
                RegionRef BndDomainRight ;
                Coefficient 1.0 ;
                Function Vector[X[] + <<dm.magnet.geometry.air_radius*2>>, Y[], Z[]] ;
            }
            {% endif %}
            {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
            {Region Omega ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }
    { Name Current ;
        Case {
            {% if dm.magnet.solve.formulation_parameters.formulation == "AI_uncoupled" %}
            {Region Cuts ; Type Assign ; Value 0. ;} // For fully uncoupled filaments !without! transport current
            {% endif %}
            {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
            {Region Cuts ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }
    { Name Current_t ;
        Case {
            {Region BndMatrixCut ; Type Assign ; Value 1.0 ; TimeFunction I_transport[] ;} // Contraint for the total transport current
        }
    }
    { Name FieldCirculation ;
        Case {
            // impose a circulation of the h-field in omegaCC
            // MAIN CHANGE: this one or the one below
            // {Region CutAirVertical ; Type Assign ; Value <<dm.magnet.geometry.air_radius>>*2 ; TimeFunction CompX[hsVal[]] ;} // impose component in x direction
            // {Region CutAirHorizontal ; Type Assign ; Value <<dm.magnet.geometry.air_radius>>*2 ; TimeFunction CompY[hsVal[]] ;} // impose component in y direction
        }
    }
    { Name FluxChange ;
        Case {
            // impose the flux change connect through b in omegaCC
            // MAIN CHANGE: this one or the one above (this one is for imposed flux, which maybe makes more sense physically)
            {% if dm.magnet.geometry.type == 'periodic_square' %}
            {Region CutAirHorizontal ; Type Assign ; Value -<<dm.magnet.geometry.air_radius>>*2 ; TimeFunction CompY[dbsdt[]] ;} // impose component in y direction
            {Region CutAirVertical ; Type Assign ; Value -<<dm.magnet.geometry.air_radius>>*2 ; TimeFunction CompX[dbsdt[]] ;} // impose component in x direction
            {% endif %}
        }
    }
    { Name Voltage ; Case {} } // Empty to avoid warnings
    { Name Voltage_t ; Case {} } // Empty to avoid warnings
    { Name Current_plane ; Case {} } // Empty to avoid warnings
    { Name Voltage_plane ;
        Case {
            // The constraint below can be useful for debugging (together with the Current one on Cuts, they uncouple the AI and TI problems in the linked-flux formulation)
            //{Region filamentBnd_1_1 ; Type Assign ; Value 1. ;} // Put just one to non-zero voltage to see a non-trivial solution
            //{Region BndFilaments ; Type Assign ; Value 0. ;} // All the other ones are forced to be zero
        }
    }
    { Name Current_Cir ; Case {} } //
    { Name Voltage_Cir ; Case {} } //

    { Name v_plane ;
        Case {
            // {Region filamentBnd_1_1 ; Type Assign ; Value 1. ;}
            // {Region BndFilaments ; Type Assign ; Value 0. ;}
            {Region MatrixPointOnBoundary ; Type Assign ; Value 0. ;}
        }
    }

    {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
    // As only the curl of the field is projected, the absolute value is unknown. We need to symmetrize the field
    { Name hp_static ;
        Case {
            // {Region CenterPoint ; Value 0.0 ;} // replaced by a Lagrange multiplier in the formulation (more general, as there might be a filament at the center!)
        }
    }
    {% endif %}

    // This is the key constraint for coupling global quantities: it contains the links between the filaments
    {Name ElectricalCircuit ; Type Network ;
        Case circuit {
            {% if len(rm.powered.Filaments.vol.numbers) % 6 == 1 %}
            // A filament in the center is treated separately.
            { Region Cut_0_0 ; Branch { 0, 0 } ; }
            { Region filamentBnd_0_0 ; Branch {1000, 0} ; }
            {% endif %}

            {% if dm.magnet.solve.formulation_parameters.two_ell_periodicity %}
                {% for layer in range(1, int( len(rm.powered.Filaments.vol.numbers)/6 ) + 1) %}
                    {% for filament in range(1, 4) %}
            { Region Cut_<<layer>>_<<2*filament>> ; Branch { <<100*layer + 2*filament-1>>, <<100*layer + (2*filament+1)%6>> } ; }
            { Region Cut_<<layer>>_<<(2*filament+1)%6>> ; Branch { <<100*layer + 2*filament>>, <<100*layer + (2*filament+1)%6+1>> } ; }

            {% if dm.magnet.solve.diffusion_barriers.enable %}
            { Region R_diffusion_barrier_<<layer>>_<<2*filament-1>> ; Branch { 1000, <<100*layer + 2*filament-1 + 10>>} ; }
            { Region filamentBnd_<<layer>>_<<2*filament-1>> ; Branch {<<100*layer + 2*filament-1 + 10>>, <<100*layer + 2*filament-1>>} ; }

            { Region R_diffusion_barrier_<<layer>>_<<2*filament>> ; Branch { 1000, <<100*layer + 2*filament + 10>>} ; }
            { Region filamentBnd_<<layer>>_<<2*filament>> ; Branch {<<100*layer + 2*filament + 10>>, <<100*layer + 2*filament>>} ; }
            {% else %}
            { Region filamentBnd_<<layer>>_<<2*filament-1>> ; Branch {1000, <<100*layer + 2*filament-1>>} ; }
            { Region filamentBnd_<<layer>>_<<2*filament>> ; Branch {1000, <<100*layer + 2*filament>>} ; }
            {% endif %}
                    {%endfor%}
                {%endfor%}

            {% else %}
                {% for layer in range(1, int( len(rm.powered.Filaments.vol.numbers)/6 ) + 1) %}
                    {% for filament in range(1, 7) %}
            { Region Cut_<<layer>>_<<filament>> ; Branch { <<100*layer + filament>>, <<100*layer + filament%6+1>> } ; }
            {% if dm.magnet.solve.diffusion_barriers.enable %}
            { Region R_diffusion_barrier_<<layer>>_<<filament>> ; Branch { 1000, <<100*layer + filament + 10>>} ; }
            { Region filamentBnd_<<layer>>_<<filament>> ; Branch {<<100*layer + filament + 10>>, <<100*layer + filament>>} ; }
            {% else %}
            { Region filamentBnd_<<layer>>_<<filament>> ; Branch {1000, <<100*layer + filament>>} ; }
            {% endif %}
                    {%endfor%}
                {%endfor%}
            {% endif %}
        }
    }
    { Name h ; Type Assign ;
        Case {
            {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
            {Region OmegaC ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }

}

FunctionSpace {
    // Function space for magnetic field h in h-conform formulation. Main field for the magnetodynamic problem.
    //  h = sum phi_n * grad(psi_n)     (nodes in Omega_CC with boundary)
    //      + sum h_e * psi_e           (edges in Omega_C)
    //      + sum I_i * c_i             (filament cuts - homology gmsh)
    //      + sum I_i2 * c_i2           (air cuts - manually computed)
    { Name h_space; Type Form1;
        BasisFunction {
            { Name gradpsin; NameOfCoef phin; Function BF_GradNode;
                Support OmegaCC_AndBnd; Entity NodesOf[OmegaCC]; } // Extend support to boundary for surface integration (e.g. useful for weak B.C.)
            { Name gradpsin; NameOfCoef phin2; Function BF_GroupOfEdges;
                Support OmegaC; Entity GroupsOfEdgesOnNodesOf[BndOmegaC]; } // To treat properly the Omega_CC-Omega_C boundary
            { Name psie; NameOfCoef he; Function BF_Edge;
                Support OmegaC_AndBnd; Entity EdgesOf[All, Not BndOmegaC]; }
            { Name ci; NameOfCoef Ii; Function BF_GroupOfEdges;
                Support Omega; Entity GroupsOfEdgesOf[Cuts]; } // The region Cuts contains the union of all the relevant cuts (cohomology basis function support)
            { Name ct; NameOfCoef It; Function BF_GroupOfEdges;
                Support Omega; Entity GroupsOfEdgesOf[BndMatrixCut]; } // The region Cuts contains the union of all the relevant cuts (cohomology basis function support)
            {% if dm.magnet.geometry.type == 'periodic_square' %}
            { Name ci2; NameOfCoef Ii2; Function BF_GradGroupOfNodes;
                Support ElementsOf[OmegaCC, OnPositiveSideOf CutAirHorizontal];
                Entity GroupsOfNodesOf[CutAirHorizontal]; }
            { Name ci2; NameOfCoef Ii3; Function BF_GroupOfEdges;
                Support OmegaC; Entity GroupsOfEdgesOf[CutAirHorizontal, InSupport CutAirHorizontalTL]; }
            { Name ci3; NameOfCoef Ii4; Function BF_GradGroupOfNodes;
                Support ElementsOf[OmegaCC, OnPositiveSideOf CutAirVertical];
                Entity GroupsOfNodesOf[CutAirVertical]; }
            { Name ci3; NameOfCoef Ii5; Function BF_GroupOfEdges;
                Support OmegaC; Entity GroupsOfEdgesOf[CutAirVertical, InSupport CutAirVerticalTL]; }
            {% endif %}
        }
        GlobalQuantity {
            { Name I ; Type AliasOf        ; NameOfCoef Ii ; }
            { Name V ; Type AssociatedWith ; NameOfCoef Ii ; }
            { Name It ; Type AliasOf        ; NameOfCoef It ; }
            { Name Vt ; Type AssociatedWith ; NameOfCoef It ; }
            {% if dm.magnet.geometry.type == 'periodic_square'%}
            { Name CirculationHorizontal ; Type AliasOf        ; NameOfCoef Ii2 ; }
            { Name FluxChangeHorizontal ; Type AssociatedWith ; NameOfCoef Ii2 ; }
            { Name CirculationVertical ; Type AliasOf        ; NameOfCoef Ii4 ; }
            { Name FluxChangeVertical ; Type AssociatedWith ; NameOfCoef Ii4 ; }
            {% endif %}
        }
        SubSpace {
            { Name c ; NameOfBasisFunction ct ; }
        }

        Constraint {
            { NameOfCoef he; EntityType EdgesOf; NameOfConstraint h; }
            { NameOfCoef phin; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef phin2; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef Ii ;
                EntityType GroupsOfEdgesOf ; NameOfConstraint Current ; }
            { NameOfCoef It ;
                EntityType GroupsOfEdgesOf ; NameOfConstraint Current_t ; }
            {% if dm.magnet.geometry.type == 'periodic_square' %}
            { NameOfCoef Ii2 ;
                EntityType GroupsOfNodesOf ; NameOfConstraint FieldCirculation ; }
            { NameOfCoef FluxChangeHorizontal ;
                EntityType GroupsOfNodesOf ; NameOfConstraint FluxChange ; }
            { NameOfCoef Ii4 ;
                EntityType GroupsOfNodesOf ; NameOfConstraint FieldCirculation ; }
            { NameOfCoef FluxChangeVertical ;
                EntityType GroupsOfNodesOf ; NameOfConstraint FluxChange ; }
            {% endif %}
            { NameOfCoef V ;
                EntityType GroupsOfNodesOf ; NameOfConstraint Voltage ; }
            { NameOfCoef Vt ;
                EntityType GroupsOfNodesOf ; NameOfConstraint Voltage_t ; }
        }
    }
    // Function space for the transverse problem voltage field. Main field for the electrokinetics problem.
    // The (transverse) coupling current derive from this voltage j_coupling = - sigma * grad(v).
    { Name v_space_elKin ; Type Form0 ;
        BasisFunction {
            { Name vn ; NameOfCoef vn ; Function BF_Node ;
                Support Matrix_partitions_for_TI ; Entity NodesOf[All, Not BndFilaments] ; }
            { Name vi; NameOfCoef vi; Function BF_GroupOfNodes;
                Support Matrix_partitions_for_TI; Entity GroupsOfNodesOf[BndFilaments]; }
            {% if dm.magnet.solve.global_diffusion_barrier.enable %}
            { Name vd ; NameOfCoef vd ; Function BF_Node ;
                Support MatrixInternalSurface ; Entity NodesOf[GlobalDiffusionBarrier] ; }
            { Name vd ; NameOfCoef vd2 ; Function BF_Node ;
                Support GlobalDiffusionBarrier ; Entity NodesOf[GlobalDiffusionBarrier] ; } // Only the discontinuous contribution must be defined on the global diffusion barrier, and nothing else (the formulation relies on this).
            {% endif %}
        }
        GlobalQuantity {
            { Name V ; Type AliasOf        ; NameOfCoef vi ; }
            { Name I ; Type AssociatedWith ; NameOfCoef vi ; }
        }
        Constraint {
            { NameOfCoef vn ; EntityType NodesOf ; NameOfConstraint v_plane ; }
            { NameOfCoef V ;
                EntityType Region ; NameOfConstraint Voltage_plane ; }
            { NameOfCoef I ;
                EntityType Region ; NameOfConstraint Current_plane ; }
        }
    }
    {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
    // The curl of this space is the projection of the coupling current on this subspace (no net current from fil.)
    { Name h_perp_space_static; Type Form1P;
        BasisFunction {
            { Name sn; NameOfCoef hn; Function BF_PerpendicularEdge;
                Support Matrix_partitions_for_TI; Entity NodesOf[All]; }
        }
        Constraint {
            { NameOfCoef hn; EntityType NodesOf; NameOfConstraint hp_static; }
        }
    }
    // This is a Lagrange multplier for forcing the integral of hp_static to be zero in the matrix (avg field = 0)
    { Name h_perp_space_static_lagrange; Type Vector;
        BasisFunction {
            { Name sn_lag; NameOfCoef hn_lag; Function BF_RegionZ;
                Support Matrix_partitions_for_TI; Entity Matrix_partitions_for_TI; } // Ideally, should be only one function (not one per matrix part). To be double-checked!
        }
    }
    // This space will correct the static space above with dynamic effects
    { Name h_perp_space_dynamic; Type Form1P;
        BasisFunction {
            { Name sn; NameOfCoef hn; Function BF_PerpendicularEdge;
                Support Matrix_partitions_for_TI; Entity NodesOf[All, Not TI_adjacent_region ]; }
        }
    }
    {% endif %}

    {% if dm.magnet.solve.diffusion_barriers.enable %}
    // Function space for the circuit domain
    { Name ElectricalCircuit; Type Scalar;
        BasisFunction {
            { Name sn; NameOfCoef Ir; Function BF_Region;
                Support Resistors_diffusion_barrier; Entity Resistors_diffusion_barrier; }
        }
        GlobalQuantity {
            { Name Iz ; Type AliasOf        ; NameOfCoef Ir ; }
            { Name Vz ; Type AssociatedWith ; NameOfCoef Ir ; }
        }
        Constraint {
            { NameOfCoef Iz ; EntityType Region ; NameOfConstraint Current_Cir ; }
            { NameOfCoef Vz ; EntityType Region ; NameOfConstraint Voltage_Cir ; }
        }
    }
    {% endif %}
}

Jacobian {
    { Name Vol ;
        Case {
            {Region All ; Jacobian Vol ;}
        }
    }
    { Name Sur ;
        Case {
            { Region All ; Jacobian Sur ; }
        }
    }
}

Integration {
    { Name Int ;
        Case {
            { Type Gauss ;
                Case {
                    { GeoElement Point ; NumberOfPoints 1 ; }
                    { GeoElement Line ; NumberOfPoints 3 ; }
                    { GeoElement Triangle ; NumberOfPoints 3 ; }
                }
            }
        }
    }
}

Formulation{
    // h-formulation
    { Name MagDyn_hphi; Type FemEquation;
        Quantity {
            // Functions for the axial current (AI) problem
            { Name h; Type Local; NameOfSpace h_space; }
            { Name hp; Type Local; NameOfSpace h_space; }
            { Name I; Type Global; NameOfSpace h_space[I]; }
            { Name V; Type Global; NameOfSpace h_space[V]; }
            { Name It; Type Global; NameOfSpace h_space[It]; }
            { Name Vt; Type Global; NameOfSpace h_space[Vt]; }
            { Name c; Type Local; NameOfSpace h_space[c]; }
            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" %}
            // Functions for the transverse current (TI) problem
            { Name v; Type Local; NameOfSpace v_space_elKin; }
            { Name Vp; Type Global; NameOfSpace v_space_elKin[V]; }
            { Name Ip; Type Global; NameOfSpace v_space_elKin[I]; }
            {% if dm.magnet.solve.diffusion_barriers.enable %}
            { Name Iz; Type Global; NameOfSpace ElectricalCircuit[Iz]; }
            { Name Vz; Type Global; NameOfSpace ElectricalCircuit[Vz]; }
            {% endif %}
            {% endif %}
            {% if dm.magnet.geometry.type == 'periodic_square' %}
            { Name CirculationHorizontal; Type Global; NameOfSpace h_space[CirculationHorizontal]; }
            { Name FluxChangeHorizontal; Type Global; NameOfSpace h_space[FluxChangeHorizontal]; }
            { Name CirculationVertical; Type Global; NameOfSpace h_space[CirculationVertical]; }
            { Name FluxChangeVertical; Type Global; NameOfSpace h_space[FluxChangeVertical]; }
            {% endif %}
        }
        Equation {
            // --- AI problem ---
            // Time derivative of b (NonMagnDomain)
            Galerkin { [ ell* mu[] * Dof{h} / $DTime , {h} ];
                In Omega; Integration Int; Jacobian Vol;  }
            Galerkin { [ - ell*mu[] * {h}[1] / $DTime , {h} ];
                In Omega; Integration Int; Jacobian Vol;  }
            // Induced current (linear OmegaC)
            Galerkin { [ ell*rho[mu0*Norm[{h}]] * Dof{d h} , {d h} ];
                In LinOmegaC; Integration Int; Jacobian Vol;  }
            // Induced current (non-linear OmegaC)
            Galerkin { [ ell*rho[{d h}, mu0*Norm[{h}]] * {d h} , {d h} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  }

            Galerkin { [ ell*dedj[{d h}, mu0*Norm[{h}]] * Dof{d h} , {d hp} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method
            Galerkin { [ - ell*dedj[{d h}, mu0*Norm[{h}]] * {d h} , {d hp} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method

            {% if 0 and dm.conductors[dm.magnet.solve.conductor_name].Jc_fit.type != 'Constant Jc' and dm.magnet.solve.general_parameters.superconductor_linear == False%}
            // We don't use this N-R for the moment (does not seem to decrease number of iterations, but is expensive for assembly -> to double-check)
            Galerkin { [ ell*dedb[{d h}, mu0*{h}] * mu0*Dof{h} , {d hp} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method
            Galerkin { [ -ell*dedb[{d h}, mu0*{h}] * mu0*{h} , {d hp} ];
                In NonLinOmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method
            {% endif %}

            // Natural boundary condition for normal flux density (useful when transport current is an essential condition)
            {% if dm.magnet.geometry.type == 'coil' or dm.magnet.geometry.type == 'strand_only'%}
            Galerkin { [ - ell*dbsdt[] * Normal[] , {dInv h} ];
                In BndAir; Integration Int; Jacobian Sur;  }
            {% endif %}

            // Global terms for imposing flux changes
            {% if dm.magnet.geometry.type == 'periodic_square' %}
            GlobalTerm { [ ell*Dof{FluxChangeHorizontal} , {CirculationHorizontal} ] ; In CutAirHorizontal ; }
            GlobalTerm { [ ell*Dof{FluxChangeVertical} , {CirculationVertical} ] ; In CutAirVertical ; }
            {% endif %}

            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" %}
            // --- TI problem ---
            Galerkin { [ ell * sigma[mu0*Norm[{h}]] * Dof{d v} , {d v} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  } // Matrix
            {% if dm.magnet.solve.global_diffusion_barrier.enable %}
            Galerkin { [ ell * 1/rho_contact[] * Dof{v} , {v} ];
                In GlobalDiffusionBarrier; Integration Int; Jacobian Sur;  } // This requires that only the discontinuous component of {v} is defined on the global diffusion barrier
            {% endif %}
            GlobalTerm { [ Dof{Ip} , {Vp} ] ; In BndFilaments ; }

            {% if dm.magnet.solve.diffusion_barriers.enable %}
            // Diffusion barriers
            GlobalTerm{ [ Dof{Vz},            {Iz} ];  In Resistors_diffusion_barrier; }
            GlobalTerm{ [ R[] * Dof{Iz},      {Iz} ];  In Resistors_diffusion_barrier; }
            // --- Coupling between AI and TI problems via circuit equations ---
            GlobalEquation {
                Type Network ; NameOfConstraint ElectricalCircuit ;
                { Node {I};  Loop {V};  Equation {V};  In Cuts ; }
                { Node {Ip}; Loop {Vp}; Equation {Ip}; In BndFilaments ; }
                { Node {Iz}; Loop {Vz}; Equation {Vz}; In Resistors_diffusion_barrier; }
          	}
            {% else %}
            // --- Coupling between AI and TI problems via circuit equations ---
            GlobalEquation {
                Type Network ; NameOfConstraint ElectricalCircuit ;
                { Node {I};  Loop {V};  Equation {V};  In Cuts ; }
                { Node {Ip}; Loop {Vp}; Equation {Ip}; In BndFilaments ; }
          	}
            {% endif %}
            {% endif %}
            // Global term (these terms apparently must be placed at the end, it is not clear why)
            GlobalTerm { [ Dof{V} , {I} ] ; In Cuts ; }
            GlobalTerm { [ Dof{Vt} , {It} ] ; In BndMatrixCut ; }
        }
    }
    {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
    // h-formulation
    { Name MagDyn_hphi_dynCorr; Type FemEquation;
        Quantity {
            // Functions for the AI and TI problems, that are just used here (and not solved for)
            { Name h; Type Local; NameOfSpace h_space; }
            { Name v; Type Local; NameOfSpace v_space_elKin; }
            // Functions for the dynamic correction of the TI problem
            { Name hp_static; Type Local; NameOfSpace h_perp_space_static; }
            { Name hp_static_lagrange; Type Local; NameOfSpace h_perp_space_static_lagrange; }
            { Name hp_dynamic; Type Local; NameOfSpace h_perp_space_dynamic; }
        }
        Equation {
            // --- Dynamic correction of the TI problem ---
            // Projection of the static current flow on the curl of a "static" magnetic field
            Galerkin { [ sigma[mu0*Norm[{h}]] * {d v} , {d hp_static} ]; // No DOF! Just take the solution of the previously solved v-based formulation
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  }
            Galerkin { [ Dof{d hp_static} , {d hp_static} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  }
            Galerkin { [ Dof{hp_static_lagrange} , {hp_static} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  }
            Galerkin { [ Dof{hp_static} , {hp_static_lagrange} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  } // ensure the magnetic field is averaged to zero over the matrix
            // Introduce a dynamic component to the magnetic field
            Galerkin { [ mu[] * Dof{hp_static} / $DTime , {hp_dynamic} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  }
            Galerkin { [ mu[] * Dof{hp_dynamic} / $DTime , {hp_dynamic} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  }
            Galerkin { [ - mu[] * {hp_static}[1] / $DTime , {hp_dynamic} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  }
            Galerkin { [ - mu[] * {hp_dynamic}[1] / $DTime , {hp_dynamic} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  }
            //Galerkin { [ - Dof{d v} , {d hp_dynamic} ];
            //    In Matrix; Integration Int; Jacobian Vol;  } // Static field is curl-free so this contribution is unnecessary!
            Galerkin { [ rho[mu0*Norm[{h}]] * Dof{d hp_dynamic} , {d hp_dynamic} ];
                In Matrix_partitions_for_TI; Integration Int; Jacobian Vol;  } // Only the dynamic correction is an eddy current
        }
    }
    {% endif %}
    {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
    // Projection formulation for initial condition
    { Name Projection_h_to_h; Type FemEquation;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
        }
        Equation{
            // For the current formulation, it seems to be accurate enough to project the field directly (and not its curl as an intermediate to reconstruct it).
            // Validity of this to be checked again if we go to different meshes between the initial condition and the following simulation
            Galerkin { [  Dof{h}, {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
            {% if dm.magnet.solve.initial_conditions.init_type == 'pos_file' %}
            Galerkin { [ - h_from_file[], {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
            {% elif dm.magnet.solve.initial_conditions.init_type == 'uniform_field' %}
            Galerkin { [ - hsVal[], {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
            {% endif %}
        }
    }
    {% endif %}
}

Macro CustomIterativeLoop
    // Compute first solution guess and residual at step $TimeStep
    Generate[A];
    Solve[A]; Evaluate[ $syscount = $syscount + 1 ];
    Generate[A]; GetResidual[A, $res0];
    Evaluate[ $res = $res0 ];
    Evaluate[ $iter = 0 ];
    Evaluate[ $convCrit = 1e99 ];
    PostOperation[MagDyn_energy];
    Print[{$iter, $res, $res / $res0, $indicFilamentLoss},
        Format "%g %14.12e %14.12e %14.12e", File infoResidualFile];
    // ----- Enter the iterative loop (hand-made) -----
    While[$convCrit > 1 && $res / $res0 <= 1e10 && $iter < iter_max]{
        Solve[A]; Evaluate[ $syscount = $syscount + 1 ];
        Generate[A]; GetResidual[A, $res];
        Evaluate[ $iter = $iter + 1 ];
        Evaluate[ $indicFilamentLossOld = $indicFilamentLoss];
        PostOperation[MagDyn_energy];
        Print[{$iter, $res, $res / $res0, $indicFilamentLoss},
            Format "%g %14.12e %14.12e %14.12e", File infoResidualFile];
        // Evaluate the convergence indicator
        Evaluate[ $relChangeACLoss = Abs[($indicFilamentLossOld - $indicFilamentLoss)/((Abs[$indicFilamentLossOld]>1e-7 || $iter < 10) ? $indicFilamentLossOld:1e-7)] ];
        Evaluate[ $convCrit = $relChangeACLoss/tol_energy];
    }
Return

Resolution {
    { Name MagDyn;
        System {
            {Name A; NameOfFormulation MagDyn_hphi;}
            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
            {Name A_dynCorr; NameOfFormulation MagDyn_hphi_dynCorr;}
            {% endif %}
        }
        Operation {
            // Initialize directories
            CreateDirectory[resDirectory];
            DeleteFile[outputPower];
            DeleteFile[infoResidualFile];
            // Initialize the solution (initial condition)
            SetTime[ timeStart ];
            SetDTime[ dt ];
            SetTimeStep[ 0 ];
            InitSolution[A];
            SaveSolution[A]; // Saves the solution x (from Ax = B) to .res file
            Evaluate[ $syscount = 0 ];
            Evaluate[ $saved = 1 ];
            Evaluate[ $elapsedCTI = 1 ]; // Number of control time instants already treated
            Evaluate[ $isCTI = 0 ];

            {% if dm.magnet.solve.formulation_parameters.compute_temperature %}
            Evaluate[ $cumulative_temperature = 0 ];
            Evaluate[ $dT_old = 0 ];
            {% endif %}

            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
            InitSolution[A_dynCorr];
            SaveSolution[A_dynCorr];
            {% else %}
            Evaluate[ $indicTotalLoss_dyn = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $indicCouplingLoss_dyn = 0 ]; // Put it to zero to avoid warnings
            {% if dm.magnet.solve.formulation_parameters.formulation != "CATI" %}
            Evaluate[ $indicCouplingLoss = 0 ]; // For conventional 2D formulation, no coupling currents and hence no coupling loss
            {% endif %}
            {% endif %}
            // ----- Enter implicit Euler time integration loop (hand-made) -----
            // Avoid too close steps at the end. Stop the simulation if the step becomes ridiculously small
            SetExtrapolationOrder[ extrapolationOrder ];
            While[$Time < timeFinal] {
                SetTime[ $Time + $DTime ]; // Time instant at which we are looking for the solution
                SetTimeStep[ $TimeStep + 1 ];
                {% if dm.magnet.solve.numerical_parameters.piecewise.force_stepping_at_times_piecewise_linear and dm.magnet.solve.source_parameters.source_type == 'piecewise'%}
                // Make sure all CTI are exactly chosen
                Evaluate[ $isCTI = 0 ];
                Test[$Time >= time_multiplier*AtIndex[$elapsedCTI]{List[control_time_instants_list]} - 1e-7 ]{
                    Evaluate[ $isCTI = 1, $prevDTime = $DTime ]; // Also save the previous time step to restart from it after the CTI
                    SetDTime[ time_multiplier*AtIndex[$elapsedCTI]{List[control_time_instants_list]} - $Time + $DTime ];
                    SetTime[ time_multiplier*AtIndex[$elapsedCTI]{List[control_time_instants_list]} ]; // To compute exactly at the asked time instant
                    Print[{$Time}, Format "*** Control time instant: %g s."];
                }
                {% endif %}
                // Iterative loop defined as a macro above
                Print[{$Time, $DTime, $TimeStep}, Format "Start new time step. Time: %g s. Time step: %g s. Step: %g."];
                Call CustomIterativeLoop;
                // Has it converged? If yes, save solution and possibly increase the time step...
                Test[ $iter < iter_max && ($res / $res0 <= 1e10 || $res0 == 0)]{
                    Print[{$Time, $DTime, $iter}, Format "Converged time %g s with time step %g s in %g iterations."];
                    // Save the solution of few time steps (small correction to avoid bad rounding)
                    // Test[ $Time >= $saved * writeInterval - 1e-7 || $Time + $DTime >= timeFinal]{
                    Test[ 1 ]{
                    // Test[ $Time >= $saved * $DTime - 1e-7 || $Time + $DTime >= timeFinal]{
                        SaveSolution[A];
                        // Post-operation for power loss quantities
                        PostOperation[test_Losses];
                        {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
                        Generate[A_dynCorr]; Solve[A_dynCorr]; SaveSolution[A_dynCorr];
                        PostOperation[test_Losses_dynCorr];
                        {% endif %}
                        Print[{$Time, $saved}, Format "Saved time %g s (saved solution number %g). Output power infos:"];
                        Print[{$Time, $indicFilamentLoss, $indicCouplingLoss, $indicEddyLoss, $indicTotalLoss, $indicCouplingLoss_dyn, $indicTotalLoss_dyn},
                            Format "%g %14.12e %14.12e %14.12e %14.12e %14.12e %14.12e", File outputPower];

                        // Compute the temperature
                        {% if dm.magnet.solve.formulation_parameters.compute_temperature == True %}
                            PostOperation[heat_capacity];
                            Evaluate[$dT = $DTime * $indicTotalLoss/$heat_capacity_per_unit_length];
                            Evaluate[ $cumulative_temperature = $cumulative_temperature + ($dT_old + $dT)/2 ];
                            Print[{$Time, $dT, $cumulative_temperature}, Format "%g %14.12e %14.12e", File outputTemperature];
                            Evaluate[ $dT_old = $dT ];
                        {% endif %}

                        Evaluate[$saved = $saved + 1];
                    }
                    {% if dm.magnet.solve.numerical_parameters.piecewise.force_stepping_at_times_piecewise_linear and dm.magnet.solve.source_parameters.source_type == 'piecewise' %}
                    // Consider the time step before the control time instant (if relevant) and increment $elapsedCTI
                    Test[ $isCTI == 1 ]{
                        Evaluate[ $elapsedCTI = $elapsedCTI + 1 ];
                        SetDTime[ $prevDTime ];
                    }
                    {% endif %}
                    // Increase the step if we converged sufficiently "fast" (and not a control time instant)
                    Test[ $iter < iter_max / 4 && $DTime < dt_max_var[] && $isCTI == 0 ]{
                        Evaluate[ $dt_new = Min[$DTime * 2, dt_max_var[]] ];
                        Print[{$dt_new}, Format "*** Fast convergence: increasing time step to %g"];
                        SetDTime[$dt_new];
                    }
                    Test[ $DTime > dt_max_var[]]{
                        Evaluate[ $dt_new = dt_max_var[] ];
                        Print[{$dt_new}, Format "*** Variable maximum time-stepping: reducing time step to %g"];
                        SetDTime[$dt_new];
                    }
                }
                // ...otherwise, reduce the time step and try again
                {
                    Evaluate[ $dt_new = $DTime / 2 ];
                    Print[{$iter, $dt_new},
                        Format "*** Non convergence (iter %g): recomputing with reduced step %g"];
                    RemoveLastSolution[A];
                    SetTime[$Time - $DTime];
                    SetTimeStep[$TimeStep - 1];
                    SetDTime[$dt_new];
                    // If it gets ridicoulously small, end the simulation, and report the information in crash file.
                    Test[ $dt_new < dt_max_var[]/1000000 ]{
                        Print[{$iter, $dt_new, $Time},
                            Format "*** Non convergence (iter %g): time step %g too small, stopping the simulation at time %g s.", File crashReportFile];
                        // Print[A];
                        Exit;
                    }
                }
            } // ----- End time loop -----
            // Print information about the resolution and the nonlinear iterations
            Print[{$syscount}, Format "Total number of linear systems solved: %g"];
        }
    }
    {% if dm.magnet.solve.initial_conditions.init_type != 'virgin' %}
    { Name Projection_h_to_h;
        System {
            {Name Projection_h_to_h; NameOfFormulation Projection_h_to_h; DestinationSystem A ;}
        }
        Operation {
            {% if dm.magnet.solve.initial_conditions.init_type == 'pos_file' %}
            GmshRead[StrCat["../", "Solution_<<dm.magnet.solve.initial_conditions.solution_to_init_from>>/", "last_magnetic_field.pos"]]; // This file has to be in format without mesh (no -v2, here with GmshParsed format)
            {% endif %}
            Generate[Projection_h_to_h]; Solve[Projection_h_to_h];
            TransferSolution[Projection_h_to_h];
        }
    }
    {% endif %}
}

PostProcessing {
    { Name MagDyn_hphi; NameOfFormulation MagDyn_hphi;
        Quantity {
            { Name phi; Value{ Local{ [ {dInv h} ] ;
                In OmegaCC_AndBnd; Jacobian Vol; } } }
            { Name h; Value{ Local{ [ {h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name b; Value{ Local{ [ mu[] * {h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name b_reaction; Value{ Local{ [ mu[] * ({h} - hsVal[]) ] ;
                In Omega; Jacobian Vol; } } }
            { Name j; Value{ Local{ [ {d h} ] ;
                In OmegaC; Jacobian Vol; } } }
            { Name jz; Value{ Local{ [ {d h} * Vector[0,0,1]] ;
                In OmegaC; Jacobian Vol; } } }
            { Name jc; Value{ Local{ [ jc[mu0*Norm[{h}]] ] ;
                In NonLinOmegaC; Jacobian Vol; } } }
            { Name rho; Value{ Local{ [ rho_power[{d h}, mu0*Norm[{h}]] ] ;
                In NonLinOmegaC; Jacobian Vol; } } }
            { Name power_filaments; Value{ Local{ [ rho[{d h}, mu0*Norm[{h}]] * {d h} * {d h} ] ; // j*e : Power (only for filaments)
                In NonLinOmegaC; Jacobian Vol; } } }
            { Name selffield_dfluxdt; Value{ Integral{ [ CompZ[rho[{d h}, mu0*Norm[{h}]] * {d h}] ] ;
                In OmegaC; Integration Int; Jacobian Vol; } } }
            { Name sigma_matrix; Value{ Local{ [ sigma[mu0*Norm[{h}]]] ;
                In Matrix; Jacobian Vol; } } }
            { Name flux_external; Value{ Integral{ [ (mu[] * {h} * {c} / I_transport[]) ] ;
                In OmegaCC; Integration Int ; Jacobian Vol; } } }
            { Name flux_internal; Value{ Integral{ [ mu[] * {h} * (UnitVectorZ[] /\ XYZ[]/Norm[XYZ[]]) / (2 * Pi * Norm[XYZ[]]) ] ;
                In OmegaC; Integration Int; Jacobian Vol; } } }
            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" %}
            // TI model quantities
            { Name j_plane; Value{ Local{ [ -1/rho[mu0*Norm[{h}]] * {d v} ] ;
            In Matrix; Jacobian Vol; } } }
            { Name v_plane; Value{ Local{ [ {v} ] ;
                In Matrix; Jacobian Vol; } } }
            { Name Ip; Value { Term{ [ {Ip} ] ; In BndFilaments; } } }
            { Name Vp; Value { Term{ [ {Vp} ] ; In BndFilaments; } } }
            { Name power_matrix;
                Value{
                    Local{ [rho[mu0*Norm[{h}]] * {d h} * {d h}] ; // j*e = rho*j^2 in matrix (eddy)
                        In Matrix ; Integration Int ; Jacobian Vol; }
                    Local{ [ (sigma[mu0*Norm[{h}]] * {d v}) * {d v}] ; // j*e = sigma*e^2 in matrix (coupling)
                        In Matrix ; Integration Int ; Jacobian Vol; }
                    {% if dm.magnet.solve.global_diffusion_barrier.enable %}
                    Local { [ 1/rho_contact[] * {v} * {v} ];
                        In GlobalDiffusionBarrier; Integration Int; Jacobian Sur;  } // This requires that only the discontinuous component of {v} is defined on the diffusion barrier
                    {% endif %}
                }
            }
            { Name couplingLoss; // Does not include (global) contribution from possible diffusion barriers around filaments
                Value{
                    Integral{ [ (sigma[mu0*Norm[{h}]] * {d v}) * {d v}] ; // j*e = sigma*e^2 in matrix
                        In Matrix ; Integration Int ; Jacobian Vol; }
                    {% if dm.magnet.solve.global_diffusion_barrier.enable %}
                    Integral { [ 1/rho_contact[] * {v} * {v} ];
                        In GlobalDiffusionBarrier; Integration Int; Jacobian Sur;  } // This requires that only the discontinuous component of {v} is defined on the diffusion barrier
                    {% endif %}
                }
            }
            {% if dm.magnet.solve.diffusion_barriers.enable %}
            { Name diffusion_barrier_loss; // Loss per unit length (W/m)
                Value{
                    Term{ [ 1/ell * R[] * {Iz} * {Iz}] ; // P = 1/ell * R*I^2 in diffusion barriers
                        In Resistors_diffusion_barrier ; }
                }
            }
            {% endif %}
            {% endif %}
            { Name eddyLoss; // NEW. Eddyloss was computed as totalLoss[matrix], which combines eddy and couplingLoss
                Value{
                    Integral{ [rho[mu0*Norm[{h}]] * {d h} * {d h}] ; // EddyLoss = rho*j^2 in matrix
                        In Matrix ; Integration Int ; Jacobian Vol; }
                }
            }
            { Name totalLoss; // Does not include (global) contribution from possible diffusion barriers around filaments
                Value{
                    // Separate OmegaC into Matrix and nonlinear (resistivities take different argument types)
                    Integral{ [rho[{d h}, mu0*Norm[{h}]] * {d h} * {d h}] ; // j*e = rho*j^2 (filaments)
                        In NonLinOmegaC ; Integration Int ; Jacobian Vol; }
                    Integral{ [rho[mu0*Norm[{h}]] * {d h} * {d h}] ; // j*e = rho*j^2 (eddy)
                        In Matrix ; Integration Int ; Jacobian Vol; }
                    {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" %}
                    Integral{ [ (sigma[mu0*Norm[{h}]]*{d v}) * {d v}] ; // j*e = sigma*e^2 in matrix (coupling)
                        In Matrix ; Integration Int ; Jacobian Vol; }
                    {% if dm.magnet.solve.global_diffusion_barrier.enable %}
                    Integral { [ 1/rho_contact[] * {v} * {v} ];
                        In GlobalDiffusionBarrier; Integration Int; Jacobian Sur;  } // This requires that only the discontinuous component of {v} is defined on the diffusion barrier
                    {% endif %}
                    {% endif %}
                }
            }
            { Name heat_capacity;
                Value{
                    Integral{ [(filament_Cv[T[] + $cumulative_temperature, mu0*Norm[{h}]] )] ; // j*e = rho*j^2 in filaments (?)
                        In NonLinOmegaC ; Integration Int ; Jacobian Vol; }
                    Integral{ [(matrix_Cv[T[] + $cumulative_temperature]) ] ; // j*e = rho*j^2 in filaments (?)
                        In NonLinOmegaC ; Integration Int ; Jacobian Vol; }
                }
            }
            { Name I; Value { Term{ [ {I} ] ; In Cuts; } } }
            { Name V; Value { Term{ [ {V} ] ; In Cuts; } } }
            { Name V_unitlen; Value { Term{ [ {V} / ell ] ; In Cuts; } } }
            { Name It; Value { Term{ [ {It} ] ; In BndMatrixCut; } } }
            { Name Vt; Value { Term{ [ {Vt} ] ; In BndMatrixCut; } } }
            { Name Vt_unitlen; Value { Term{ [ {Vt} / ell ] ; In BndMatrixCut; } } }
            { Name I_integral;
                Value{
                    Integral{ [ {d h} * Vector[0,0,1]] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                }
            }
            { Name I_abs_integral;
                Value{
                    Integral{ [ Fabs[{d h} * Vector[0,0,1]]] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                }
            }
            { Name area;
                Value{
                    Integral{ [ 1 ] ;
                        In Omega ; Integration Int ; Jacobian Vol; }
                }
            }
            // Applied field (useful for magnetization plots)
            { Name hsVal; Value{ Term { [ hsVal[] ]; In Omega; } } }
            // Magnetization: integral of 1/2 * (r /\ j) in a conducting (sub-)domain
            { Name magnetization; Value{ Integral{ [ 0.5 * XYZ[] /\ {d h} ] ;
                In OmegaC; Integration Int; Jacobian Vol; } } }
            // Magnetic energy
            { Name magnetic_energy; Value{ Integral{ [ 0.5 * mu[] * {h} * {h} ] ;
                In Omega; Integration Int; Jacobian Vol; } } }
            { Name b_integral; Value{ Integral{ [ mu[] * {h} ] ;
                In Omega; Integration Int; Jacobian Vol; } } }
        }
    }
    {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
    { Name MagDyn_hphi_dynCorr; NameOfFormulation MagDyn_hphi_dynCorr;
        Quantity {
            { Name hp_static; Value{ Local{ [ {hp_static} ] ;
                In Matrix_partitions_for_TI; Jacobian Vol; } } }
            { Name hp_static_lagrange; Value{ Local{ [ {hp_static_lagrange} ] ;
                In Matrix_partitions_for_TI; Jacobian Vol; } } }
            { Name j_static; Value{ Local{ [ {d hp_static} ] ;
                In Matrix_partitions_for_TI; Jacobian Vol; } } }
            { Name hp_dynamic; Value{ Local{ [ {hp_dynamic} ] ;
                In Matrix_partitions_for_TI; Jacobian Vol; } } }
            { Name j_dynamic; Value{ Local{ [ {d hp_dynamic} ] ;
                In Matrix_partitions_for_TI; Jacobian Vol; } } }
            { Name j_stadyn; Value{ Local{ [ {d hp_static} + {d hp_dynamic} ] ;
                In Matrix_partitions_for_TI; Jacobian Vol; } } }
            { Name j_stadyn_mixed; Value{ Local{ [ - sigma[mu0*Norm[{h}]] * {d v} + {d hp_dynamic} ] ;
                In Matrix_partitions_for_TI; Jacobian Vol; } } }
            { Name totalLoss_dyn; // Does not include (global) contribution from possible diffusion barriers around filaments
                Value{
                    // Integral{ [rho[{d h}, mu0*Norm[{h}]] * {d h} * {d h}] ;
                    //     In OmegaC ; Integration Int ; Jacobian Vol; }
                    // NEW separate OmegaC into Matrix and nonlinear
                    Integral{ [rho[{d h}, mu0*Norm[{h}]] * {d h} * {d h}] ; // j*e = rho*j^2 in filaments
                        In NonLinOmegaC ; Integration Int ; Jacobian Vol; }
                    Integral{ [rho[mu0*Norm[{h}]] * {d h} * {d h}] ; // Eddy
                        In Matrix ; Integration Int ; Jacobian Vol; }
                    Integral{ [ (- sigma[mu0*Norm[{h}]]*{d v} + {d hp_dynamic}) * (- {d v} + rho[mu0*Norm[{h}]] * {d hp_dynamic})] ;
                        In Matrix_partitions_for_TI ; Integration Int ; Jacobian Vol; } // Attention to signs!
                    {% if dm.magnet.solve.global_diffusion_barrier.enable %}
                    Integral { [ 1/rho_contact[] * {v} * {v} ];
                        In GlobalDiffusionBarrier; Integration Int; Jacobian Sur;  } // This requires that only the discontinuous component of {v} is defined on the diffusion barrier
                    {% endif %}
                }
            }
            { Name couplingLoss_dyn; // Does not include (global) contribution from possible diffusion barriers around filaments
                Value{
                    Integral{ [(- sigma[mu0*Norm[{h}]]*{d v} + {d hp_dynamic}) * (- {d v} + rho[mu0*Norm[{h}]] * {d hp_dynamic})] ;
                        In Matrix_partitions_for_TI ; Integration Int ; Jacobian Vol; } // Attention to signs!
                    {% if dm.magnet.solve.global_diffusion_barrier.enable %}
                    Integral { [ 1/rho_contact[] * {v} * {v} ];
                        In GlobalDiffusionBarrier; Integration Int; Jacobian Sur;  } // This requires that only the discontinuous component of {v} is defined on the diffusion barrier
                    {% endif %}
                }
            }
        }
    }
    {% endif %}
}

PostOperation {
    { Name MagDyn;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            {% set units_dict = {
                "b": "T",
                "b_reaction": "T",
                "h": "A/m",
                "hsVal": "A/m",
                "phi": "A",
                "power_filaments": "W",
                "power_matrix": "W",
                "j": "A/m2",
                "jz": "A/m2",
                "jc": "A/m2",
                "jPlane": "A/m2",
                "vPlane": "V/m",
                "sigma_matrix": "S/m",
                "j_dynamic": "A/m2",
                "j_stadyn_mixed": "A/m2",
                "hp_dynamic": "A/m",
                "hp_static": "A/m",
                "hp_static_lagrange": "A/m",
            } %}
            // Print[ phi, OnElementsOf OmegaCC , File StrCat["phi_f.pos"], Name "phi [A]" ];
            // Print[ b_reaction, OnElementsOf Omega , File StrCat["br.pos"], Name "br [T]" ];
            // Print[ j, OnElementsOf OmegaC , File StrCat["j.pos"], Name "j [A/m2]" ];
            // Print[ jz, OnElementsOf OmegaC , File StrCat["jz.pos"], Name "jz [A/m2]" ];
            //Print[ jc, OnElementsOf NonLinOmegaC , File StrCat["jc.pos"], Name "jc [A/m2]" ];
            //Print[ rho, OnElementsOf NonLinOmegaC , File StrCat["rho.pos"], Name "rho [Ohm.m]" ];
            // Print[ j_plane, OnElementsOf Matrix , File StrCat["jPlane.pos"], Name "j_plane [A/m2]" ];
            // Print[ v_plane, OnElementsOf Matrix , File StrCat["vPlane.pos"], Name "v_plane [V/m]" ];
            // Print[ power_filaments, OnElementsOf NonLinOmegaC , File StrCat["powFil_f.pos"], Name "powerFilaments [W]" ];
            // Print[ power_matrix, OnElementsOf Matrix , File StrCat["powMat_f.pos"], Name "powerMatrix [W]" ];
            // Print[ sigma_matrix, OnElementsOf Matrix , File StrCat["sigmaMat_f.pos"], Name "sigmaMatrix [S/m]" ];
            // Print[ b, OnElementsOf Omega , File StrCat["b.pos"], Name "b [T]" ];
            // Global solutions
            Print[ b_integral[Omega], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/b_integral.txt"]];
            Print[ It, OnRegion BndMatrixCut, File StrCat[resDirectory,"/I_transport.txt"], Format SimpleTable];
            Print[ Vt, OnRegion BndMatrixCut, File StrCat[resDirectory,"/V_transport.txt"], Format SimpleTable];
            Print[ Vt_unitlen, OnRegion BndMatrixCut, File StrCat[resDirectory,"/V_transport_unitlen.txt"], Format SimpleTable];
            Print[ hsVal[Omega], OnRegion Matrix, Format TimeTable, File StrCat[resDirectory, "/hs_val.txt"]];
            Print[ area[NonLinOmegaC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/area_sc_filaments.txt"]];
            Print[ area[Filament_holes], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/area_filament_holes.txt"]];
            Print[ area[Matrix], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/area_matrix.txt"]];
            {% for i, matrix_partition_material in zip(range(len(rm.induced.Matrix.vol.numbers)), rm.induced.Matrix.vol.names)%}
                Print[ area[Matrix_<<i>>], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/area_matrix_<<i>>.txt"]];
            {%endfor%}
            Print[ magnetization[Filaments_SC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/magn_fil.txt"]];
            Print[ magnetization[Matrix], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/magn_matrix.txt"]];
            Print[ magnetization[OmegaC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/magn_total.txt"]];
            Print[ flux_external[OmegaCC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/flux_external.txt"]];
            Print[ flux_internal[OmegaC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/flux_internal.txt"]];
            Print[ magnetic_energy[OmegaC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/magnetic_energy_internal.txt"]];
            Print[ magnetic_energy[OmegaCC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/magnetic_energy_external.txt"]];
            Print[ selffield_dfluxdt[Filaments_SC], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/selffield_dfluxdt.txt"]];
            // Local field solutions
            {% for quantity, region in zip(dm.magnet.postproc.pos_files.quantities, dm.magnet.postproc.pos_files.regions) %}
                Print[ <<quantity>>, OnElementsOf <<region>> , File StrCat["<<quantity>>_<<region>>.pos"], Name "<<quantity>> [<<units_dict[quantity]>>]" ];
            {% endfor %}
            {% if dm.magnet.postproc.compute_current_per_filament == True %}
            // Integrals of local quantities
            Print[I_integral[filament_1_1], OnGlobal, File StrCat[resDirectory,"/I_integral.txt"], Format SimpleTable];
            For i In {1:number_of_layers}
                For j In {((i==1)?2:1):6}
                    Print[I_integral[filament~{i}~{j}], OnGlobal, File > StrCat[resDirectory,"/I_integral.txt"], Format SimpleTable];
                EndFor
            EndFor
            Print[I_abs_integral[filament_1_1], OnGlobal, File StrCat[resDirectory,"/I_abs_integral.txt"], Format SimpleTable];
            For i In {1:number_of_layers}
                For j In {((i==1)?2:1):6}
                    Print[I_abs_integral[filament~{i}~{j}], OnGlobal, File > StrCat[resDirectory,"/I_abs_integral.txt"], Format SimpleTable];
                EndFor
            EndFor
            // Global quantities (axial current problem)
            Print[I, OnRegion Cut_1_1, File StrCat[resDirectory,"/I.txt"], Format SimpleTable];
            For i In {1:number_of_layers}
                For j In {((i==1)?2:1):6}
                    Print[I, OnRegion Cut~{i}~{j}, File > StrCat[resDirectory,"/I.txt"], Format SimpleTable];
                EndFor
            EndFor
            Print[V, OnRegion Cut_1_1, File StrCat[resDirectory,"/V.txt"], Format SimpleTable];
            For i In {1:number_of_layers}
                For j In {((i==1)?2:1):6}
                    Print[V, OnRegion Cut~{i}~{j}, File > StrCat[resDirectory,"/V.txt"], Format SimpleTable];
                EndFor
            EndFor
            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" %}
            // Global quantities (transverse current problem)
            Print[Ip, OnRegion filamentBnd_1_1, File StrCat[resDirectory,"/Ip.txt"], Format SimpleTable];
            For i In {1:number_of_layers}
                For j In {((i==1)?2:1):6}
                    Print[Ip, OnRegion filamentBnd~{i}~{j}, File > StrCat[resDirectory,"/Ip.txt"], Format SimpleTable];
                EndFor
            EndFor
            Print[Vp, OnRegion filamentBnd_1_1, File StrCat[resDirectory,"/Vp.txt"], Format SimpleTable];
            For i In {1:number_of_layers}
                For j In {((i==1)?2:1):6}
                    Print[Vp, OnRegion filamentBnd~{i}~{j}, File > StrCat[resDirectory,"/Vp.txt"], Format SimpleTable];
                EndFor
            EndFor
            {% endif %}
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.diffusion_barriers.enable %}
            // Gives loss per unit length, first column for time, then one column per filament boundary
            Print[ diffusion_barrier_loss, OnRegion Resistors_diffusion_barrier, Format TimeTable, File StrCat[resDirectory, "/power_diffusion_barrier.txt"]];
            {% endif %}

            // Last magnetic field solution for projection. Always saved. Note the special format GmshParsed required for proper GmshRead[] operation in the later pre-resolution.
            Print[ h, OnElementsOf Omega, Format GmshParsed , File "last_magnetic_field.pos", Name "h [A/m]", LastTimeStepOnly ];
        }
    }
    {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
    { Name MagDyn_dynCorr;
        NameOfPostProcessing MagDyn_hphi_dynCorr;
        Operation {
            // Print[ j_dynamic, OnElementsOf Matrix_partitions_for_TI , File StrCat["j_dynamic.pos"], Name "j_dynamic [A/m2]" ];
            // Print[ j_stadyn_mixed, OnElementsOf Matrix_partitions_for_TI , File StrCat["j_stadyn_mixed.pos"], Name "j_stadyn_mixed [A/m2]" ];
            // Print[ hp_dynamic, OnElementsOf Matrix_partitions_for_TI , File StrCat["hp_dynamic.pos"], Name "hp_dynamic [A/m]" ];
            // Print[ hp_static, OnElementsOf Matrix , File StrCat["hp_static.pos"], Name "hp_static [A/m]" ];
            // Print[ hp_static_lagrange, OnElementsOf Matrix , File StrCat["hp_static_lagrange.pos"], Name "hp_static_lagrange [A/m]" ];
        }
    }
    {% endif %}
    { Name MagDyn_energy; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ totalLoss[NonLinOmegaC], OnGlobal, Format Table, StoreInVariable $indicFilamentLoss, File StrCat[resDirectory,"/dummy.txt"] ];
        }
    }
    { Name test_Losses; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ totalLoss[OmegaC], OnGlobal, Format Table, StoreInVariable $indicTotalLoss, File > StrCat[resDirectory,"/dummy.txt"] ];
            Print[ totalLoss[NonLinOmegaC], OnGlobal, Format Table, StoreInVariable $indicFilamentLoss, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ eddyLoss[Matrix], OnGlobal, Format Table, StoreInVariable $indicEddyLoss, File > StrCat[resDirectory,"/dummy.txt"] ];
            {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" %}
            Print[ couplingLoss[Matrix], OnGlobal, Format Table, StoreInVariable $indicCouplingLoss, File > StrCat[resDirectory,"/dummy.txt"] ];
            {% endif %}
        }
    }

    { Name heat_capacity; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ heat_capacity[OmegaC], OnGlobal, Format Table, StoreInVariable $heat_capacity_per_unit_length, File StrCat[resDirectory,"/dummy.txt"] ];
        }
    }

    {% if dm.magnet.solve.formulation_parameters.formulation == "CATI" and dm.magnet.solve.formulation_parameters.dynamic_correction == True %}
    { Name test_Losses_dynCorr; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi_dynCorr;
        Operation {
            Print[ totalLoss_dyn[OmegaC], OnGlobal, Format Table, StoreInVariable $indicTotalLoss_dyn, File > StrCat[resDirectory,"/dummy.txt"] ];
            Print[ couplingLoss_dyn[Matrix_partitions_for_TI], OnGlobal, Format Table, StoreInVariable $indicCouplingLoss_dyn, File > StrCat[resDirectory,"/dummy.txt"] ];
        }
    }
    {% endif %}
}
