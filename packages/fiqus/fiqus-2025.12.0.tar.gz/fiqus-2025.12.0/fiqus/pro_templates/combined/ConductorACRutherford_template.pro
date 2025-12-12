Group {
    // ------- PROBLEM DEFINITION -------
    // Filaments
    Strands = Region[{<<rm.powered.Strands.vol.numbers|join(', ')>>}];
    BndStrands = Region[{<<rm.powered.Strands.surf.numbers|join(', ')>>}];

    // Individual regions for the strands
    {% for i in range(0, len(rm.powered.Strands.vol.numbers)) %}
    Strand_<<i+1>> = Region[{<<rm.powered.Strands.vol.numbers[i]>>}];
    StrandBnd_<<i+1>> = Region[{<<rm.powered.Strands.surf.numbers[i]>>}];
    {% endfor %}

    Coating = Region[{<<rm.powered.Coating.vol.numbers[0]>>}];
    CoatingBnd = Region[{<<rm.powered.Coating.surf_out.numbers[0]>>}];

    Air = Region[ {<<rm.air.vol.number>>} ];
    BndAir = Region[ {<<rm.air.surf.number>>} ];
    InnerBndAir = Region[ {<<rm.air.point.numbers|join(', ')>>} ];

    Coils = Region[{<<rm.powered.ExcitationCoils.vol.numbers|join(', ')>>}];
    BndCoils = Region[{<<rm.powered.ExcitationCoils.surf.numbers|join(', ')>>}];
    {% for i in range(0, len(rm.powered.ExcitationCoils.vol.numbers)) %}
    Coil_<<i+1>> = Region[{<<rm.powered.ExcitationCoils.vol.numbers[i]>>}];
    CoilBnd_<<i+1>> = Region[{<<rm.powered.ExcitationCoils.surf.numbers[i]>>}];
    {% endfor %}

    // Cuts
    StrandCuts = Region[{<<rm.powered.Strands.cochain.numbers|join(', ')>>}];
    CoatingCut = Region[{<<rm.powered.Coating.cochain.numbers[0]>>}]; // Coating cut
    CoilCuts = Region[{<<rm.powered.ExcitationCoils.cochain.numbers|join(', ')>>}];
    Cuts = Region[{StrandCuts, CoatingCut, CoilCuts}]; // All the cuts
    // Individual cuts for the strands
    {% for i in range(0, len(rm.powered.Strands.cochain.numbers)) %}
    Cut_<<i+1>> = Region[{<<rm.powered.Strands.cochain.numbers[i]>>}];
    {% endfor %}
    // Individual cuts for the strands
    {% for i in range(0, len(rm.powered.ExcitationCoils.cochain.numbers)) %}
    CutCoil_<<i+1>> = Region[{<<rm.powered.ExcitationCoils.cochain.numbers[i]>>}];
    {% endfor %}

    // Split into conducting and non-conducting domains, discriminating between stranded regions and massive ones
    LinOmegaC = Region[ {Coating} ];
    {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
    NonLinOmegaC = Region[ {} ];
    OmegaC_stranded = Region[ {Strands} ];
    BndOmegaC_stranded = Region[ {BndStrands} ];
    {% else %}
    NonLinOmegaC = Region[ {Strands} ];
    OmegaC_stranded = Region[ {} ];
    BndOmegaC_stranded = Region[ {} ];
    {% endif %}
    
    {% if dm.magnet.solve.formulation_parameters.rohm %}
    MagnLinDomain = Region[ {Air, Coating, Coils} ];
    MagnHystDomain = Region[ {Strands} ];
    {% else %}
    MagnLinDomain = Region[ {Air, Coating, Strands, Coils} ];
    MagnHystDomain = Region[ {} ];
    {% endif %}

    BndOmegaC = Region[ {CoatingBnd, InnerBndAir, BndStrands} ];
    OmegaC = Region[ {LinOmegaC, NonLinOmegaC} ];
    OmegaCC = Region[ {Air, OmegaC_stranded, Coils} ];
    OmegaC_and_stranded = Region[ {OmegaC, OmegaC_stranded} ];
    Omega = Region[ {OmegaC, OmegaCC} ]; // the whole domain (only surfaces in 2D)

    OmegaC_AndBnd = Region[{OmegaC, BndOmegaC}]; // useful for function space definition (support of shape functions extended to the boundaries of domains)
    OmegaCC_AndBnd = Region[{OmegaCC, BndOmegaC, BndAir}]; // idem
    
    // Here we define points on the boundaries of the filaments and the outer matrix boundary. These points are used to fix the magnetic potential to zero on the boundaries.
    StrandPointsOnBoundaries = Region[{<<rm.powered.Strands.curve.numbers|join(', ')>>}];
    CoatingPointsOnBoundaries = Region[{<<rm.powered.Coating.curve.numbers[0]>>}];
    ArbitraryPoints = Region[{CoatingPointsOnBoundaries, 9}];

    // Resistors for crossing contact resistance (by contrast with what is done in https://ieeexplore.ieee.org/abstract/document/10812063, oblique resistance are not used separately, but considered directly in the crossing ones)
    Resistors_crossing = Region[{}];
    {% for i in range(1, int(len(rm.powered.Strands.cochain.numbers)/2)) %}
    R_crossing_<<i>> = Region[{<<5000+i>>}];
    Resistors_crossing += Region[{R_crossing_<<i>>}];
    {% endfor %}

    // Resistors for adjacent contact resistance
    Resistors_adjacent = Region[{}];
    {% for i in range(1, len(rm.powered.Strands.vol.numbers)+1) %}
    R_adjacent_<<i>> = Region[{<<10000+i>>}];
    Resistors_adjacent += Region[{R_adjacent_<<i>>}];
    {% endfor %}

    Resistors = Region[{Resistors_crossing, Resistors_adjacent}];

    {% if dm.magnet.solve.source_parameters.parallel_resistor %}
    // Regions for electrical circuit for transport current and voltage
    CurrentSource = Region[ {10000000} ];
    PoweringCircuit = Region[ {CurrentSource} ]; // Groups containg all circuit elements for the transport current
    ParallelResistor = Region[ {10000001} ];
    PoweringCircuit += Region[ {ParallelResistor} ];
    {% endif %}
}

Function{
    // ------- GEOMETRY PARAMETERS -------
    N_strands = <<len(rm.powered.Strands.vol.numbers)>>; // Number of strands
    N_crossing_resistors = N_strands/2 - 1; // Number of crossing resistors
    ell = 1.0 * <<dm.conductors[dm.magnet.solve.conductor_name].cable.strand_twist_pitch>> / <<len(rm.powered.Strands.vol.numbers)>>; // Periodicity length

    // ------- MATERIAL PARAMETERS - MAGNETIC -------
    mu0 = Pi*4e-7; // [H/m]
    nu0 = 1.0/mu0; // [m/H]
    
    // Further steps to be done in case this model is used as a standalone model (not done here as the nonlinear version of this Rutherford model is currently only used
    // as a verification model for the HomogenizedConductor model, so the current implementation is kept for simplicity, for now): 
    //      - template all this with parameters from input files, and free numbers of cells, for both ROHM and ROHF
    //      - use compiled C++ functions instead of scripted ones as below (as is done for HomogenizedConductor)
    //      - include I-dependence in ROHM (not trivial since it combines local and global quantities)
    //      - include b-dependence in ROHF & PL/current sharing (for Ic and coercivity, not trivial for the same reason as above)
    //      - include temperature dependence in ROHM, ROHF, and other material parameters (easy if we assume uniform temperature)
    {% if dm.magnet.solve.formulation_parameters.rohm %}
    mu[Coating] = mu0;
    nu[Coating] = nu0;
    mu[Air] = mu0;
    nu[Air] = nu0;
    mu[Coils] = mu0;
    nu[Coils] = nu0;
    // ROHM Model for strands
    N = 5;
    // Weights (-)
    w_1 = 0.23;
    w_2 = 0.31;
    w_3 = 0.29;
    w_4 = 0.13;
    w_5 = 0.04;
    // Uncoupled irreversibility parameter (A/m)
    kappa_1 = 0; // A/m, first one must be zero, this is mandatory
    kappa_2 = 0; // A/m
    kappa_3 = 0.25/mu0; // A/m
    kappa_4 = 0.5/mu0; // A/m
    kappa_5 = 0.75/mu0; // A/m
    // Coupled (minus uncoupled) irreversibility parameter (A/m)
    chi_1 = 0; // A/m, first one must be zero, this is mandatory
    chi_2 = 1.5/mu0; // A/m
    chi_3 = 0.7/mu0; // A/m
    chi_4 = 1.2/mu0; // A/m
    chi_5 = 1.2/mu0; // A/m
    // Coupling time constants (s)
    tau_c_Val = 0.35; // s
    tau_c_1 = 0;
    tau_c_2 = 0.5*tau_c_Val;
    tau_c_3 = tau_c_Val;
    tau_c_4 = tau_c_Val;
    tau_c_5 = tau_c_Val;
    // Eddy current time constants (s)
    tau_e_Val = 1e-4; // s
    tau_e_1 = tau_e_Val;
    tau_e_2 = tau_e_Val;
    tau_e_3 = tau_e_Val;
    tau_e_4 = tau_e_Val;
    tau_e_5 = tau_e_Val;
    // Multiplier for the field-dependent irreversibilty parameter
    list_f_kappa = {0.00000000e+00, 1.00000000e+00, 9.39597315e-02, 9.70532886e-01,
        1.87919463e-01, 9.08385278e-01, 2.81879195e-01, 8.25986815e-01,
        3.75838926e-01, 7.38862115e-01, 4.69798658e-01, 6.63868696e-01,
        5.63758389e-01, 6.07033231e-01, 6.57718121e-01, 5.62773567e-01,
        7.51677852e-01, 5.26772394e-01, 8.45637584e-01, 4.96552160e-01,
        9.39597315e-01, 4.70616295e-01, 1.03355705e+00, 4.47956409e-01,
        1.12751678e+00, 4.27859492e-01, 1.22147651e+00, 4.09816324e-01,
        1.31543624e+00, 3.93747334e-01, 1.40939597e+00, 3.79298723e-01,
        1.50335570e+00, 3.66109142e-01, 1.59731544e+00, 3.53990385e-01,
        1.69127517e+00, 3.42796324e-01, 1.78523490e+00, 3.32399089e-01,
        1.87919463e+00, 3.22699151e-01, 1.97315436e+00, 3.13616338e-01,
        2.06711409e+00, 3.05079435e-01, 2.16107383e+00, 2.97028765e-01,
        2.25503356e+00, 2.89415278e-01, 2.34899329e+00, 2.82196893e-01,
        2.44295302e+00, 2.75334654e-01, 2.53691275e+00, 2.68796409e-01,
        2.63087248e+00, 2.62555621e-01, 2.72483221e+00, 2.56585778e-01,
        2.81879195e+00, 2.50864851e-01, 2.91275168e+00, 2.45374155e-01,
        3.00671141e+00, 2.40096149e-01, 3.10067114e+00, 2.35014644e-01,
        3.19463087e+00, 2.30115890e-01, 3.28859060e+00, 2.25388074e-01,
        3.38255034e+00, 2.20818839e-01, 3.47651007e+00, 2.16397919e-01,
        3.57046980e+00, 2.12116612e-01, 3.66442953e+00, 2.07965874e-01,
        3.75838926e+00, 2.03937695e-01, 3.85234899e+00, 2.00025201e-01,
        3.94630872e+00, 1.96221977e-01, 4.04026846e+00, 1.92521514e-01,
        1.07114094e+01, 4.22119189e-02, 1.08053691e+01, 4.07794262e-02,
        1.08993289e+01, 3.93539509e-02, 1.09932886e+01, 3.79351159e-02,
        1.10872483e+01, 3.65225668e-02, 1.11812081e+01, 3.51159648e-02,
        1.12751678e+01, 3.37149413e-02, 1.13691275e+01, 3.23190965e-02,
        1.14630872e+01, 3.09280383e-02, 1.15570470e+01, 2.95413741e-02,
        1.16510067e+01, 2.81586397e-02, 1.17449664e+01, 2.67793730e-02,
        1.18389262e+01, 2.54030907e-02, 1.19328859e+01, 2.40292464e-02,
        1.20268456e+01, 2.26572523e-02, 1.21208054e+01, 2.12864688e-02,
        1.22147651e+01, 1.99161765e-02, 1.23087248e+01, 1.85455626e-02,
        1.24026846e+01, 1.71737023e-02, 1.24966443e+01, 1.57994954e-02,
        1.25906040e+01, 1.44216598e-02, 1.26845638e+01, 1.30386263e-02,
        1.27785235e+01, 1.16483848e-02, 1.28724832e+01, 1.02483184e-02,
        1.29664430e+01, 8.83483853e-03, 1.30604027e+01, 7.40244796e-03,
        1.31543624e+01, 5.94103353e-03, 1.32483221e+01, 4.45222537e-03,
        1.33422819e+01, 3.13219576e-03, 1.34362416e+01, 2.03642832e-03,
        1.35302013e+01, 1.16778951e-03, 1.36241611e+01, 5.31251257e-04,
        1.37181208e+01, 1.36044320e-04, 1.38120805e+01, 5.43279830e-07,
        1.39060403e+01, 0.00000000e+00, 1.40000000e+01, 0.00000000e+00};
    // Field-dependent parameters
    f_kappa[] = InterpolationLinear[$1]{List[list_f_kappa]}; // TO DO: refine this scaling and introduce dependence on transport current if this model is used as standalone
    f_chi[] = (1 - $1/14)/(1 + $1/5); // TO DO: same

    // --- Test for a hysteresis element: gives the reversible field in the static case
    // $1: new field
    // $2: previous reversible field
    // $3: irreversibility parameter
    U[] = (Norm[$1 - $2] <= $3) ? $2 : ($1 - $3 * ($1 - $2) / Norm[$1 - $2]);
    // Derivative w.r.t. new field
    dUdh[] = (Norm[$1 - $2]#9 <= $3) ? TensorSym[0., 0., 0., 0., 0., 0.] : 
                                        (TensorSym[1., 0., 0., 1., 0., 1.] - $3 / #9 * (TensorSym[1., 0., 0., 1., 0., 1.] -  SquDyadicProduct[$1-$2] / (#9)^2 ));
    // --- Test for a hysteresis element: gives the r+e+c field in the dynamic case
    // $1: new field
    // $2: previous reversible field
    // $3: previous rev+eddy+coupling field
    // $4: irreversibility parameter
    Urec[] = (Norm[$1 - $3] <= $4 && ( ($1 - $2) * (($1 - $2)*Norm[$1 - $2] - $4 * ($1 - $2))) <= 0) ? $2 : ($1 - $4 * ($1 - $2) / Norm[$1 - $2]);
    // Derivative w.r.t. new field
    dUrecdh[] = (Norm[$1 - $3] <= $4 && ( ($1 - $2) * (($1 - $2)*Norm[$1 - $2] - $4 * ($1 - $2))) <= 0) ? TensorSym[0., 0., 0., 0., 0., 0.] : 
                                        (TensorSym[1., 0., 0., 1., 0., 1.] - $4 / (Norm[$1-$2]) * (TensorSym[1., 0., 0., 1., 0., 1.] -  SquDyadicProduct[$1-$2] / (Norm[$1-$2])^2 ));

    // --- Functions for one cell only
    // Function for reversible field only, for one cell
    // $1: new field
    // $2: reversible field at previous time step
    // $3: rev+eddy+coupling field at previous time step
    // $4: w_k,         weight for the considered cell k
    // $5: kappa_k,     uncoupled irreversibility parameter for the considered cell k
    // $6: chi_k,       coupled (minus uncoupled) irreversibility parameter for the considered cell k
    // $7: tau_c_k,     coupling current time constant for the considered cell k
    // $8: tau_e_k,     eddy current time constant for the considered cell k
    // hrev_k[] = (U[$1, $3, $5] + (tau_e/$DTime)#1*$2)/(1+#1) ;
    hrev_k[] = (($7/$DTime)#1 * Norm[Urec[$1, $2, $3, $5] - $2]#3 <= $6 * (1 + #1 + ($8/$DTime)#2)) ?
                    (Urec[$1, $2, $3, $5] + (#1+#2)*$2)/(1+#1+#2) :
                    (Urec[$1, $2, $3, $5] - $6*(Urec[$1, $2, $3, $5] - $2)/(#3) + #2*$2)/(1+#2); // Careful here division by norm (cannot be exactly zero because of the test above, but could be very small for the first cell!)
    // Function for rev+eddy+coupling field, for one cell
    // $1: new field
    // $2: reversible field at previous time step
    // $3: rev+eddy+coupling field at previous time step
    // $4: irreversibility parameter for the considered cell k
    g_k[] = Urec[$1, $2, $3, $4];
    // Derivative of the reversible field, for one cell
    // Same parameters as the function for the reversible field $1 -> $8
    dhrev_k[] = (($7/$DTime)#1 * Norm[Urec[$1, $2, $3, $5] - $2]#3 <= $6 * (1 + #1 + ($8/$DTime)#2)) ?
                    (dUrecdh[$1, $2, $3, $5])/(1+#1+#2) :
                    (dUrecdh[$1, $2, $3, $5] - $6 * 1/(#3)*(TensorSym[1., 0., 0., 1., 0., 1.]-SquDyadicProduct[Urec[$1, $2, $3, $5]-$2]/(#3)^2) * dUrecdh[$1, $2, $3, $5])/(1+#2);
    // Coupling field from time derivative of flux density b_k
    // $1: \dot b_k
    // $2: norm of b
    // $3: tau_c_k
    // $4: chi_k
    hcoupling[] = ($3/mu0 * Norm[$1] <= f_chi[$2] * $4) ? $3/mu0 * $1 : f_chi[$2] * $4 * $1 / Norm[$1];

    // --- Main hysteresis law
    // $1: new field
    // $2*k: reversible field at previous time step for cell k
    // $2*k+1: g = rev+eddy+coupling field at previous time step for cell k
    // $2*N+2: norm of b, for field-dependent parameters
    bhyst[] = mu0 * ( w_1 * hrev_k[$1, $2, $3, w_1, f_kappa[$12]*kappa_1, f_chi[$12]*chi_1, tau_c_1, tau_e_1]
                    + w_2 * hrev_k[$1, $4, $5, w_2, f_kappa[$12]*kappa_2, f_chi[$12]*chi_2, tau_c_2, tau_e_2]
                    + w_3 * hrev_k[$1, $6, $7, w_3, f_kappa[$12]*kappa_3, f_chi[$12]*chi_3, tau_c_3, tau_e_3]
                    + w_4 * hrev_k[$1, $8, $9, w_4, f_kappa[$12]*kappa_4, f_chi[$12]*chi_4, tau_c_4, tau_e_4]
                    + w_5 * hrev_k[$1, $10,$11,w_5, f_kappa[$12]*kappa_5, f_chi[$12]*chi_5, tau_c_5, tau_e_5]);
    // Derivative w.r.t. new field
    dbhystdh[] = mu0 * ( w_1 * TensorDiag[1., 1., 1.]/(1+tau_e_1/$DTime)
                    + w_2 * dhrev_k[$1, $4, $5, w_2, f_kappa[$12]*kappa_2, f_chi[$12]*chi_2, tau_c_2, tau_e_2]
                    + w_3 * dhrev_k[$1, $6, $7, w_3, f_kappa[$12]*kappa_3, f_chi[$12]*chi_3, tau_c_3, tau_e_3]
                    + w_4 * dhrev_k[$1, $8, $9, w_4, f_kappa[$12]*kappa_4, f_chi[$12]*chi_4, tau_c_4, tau_e_4]
                    + w_5 * dhrev_k[$1, $10,$11,w_5, f_kappa[$12]*kappa_5, f_chi[$12]*chi_5, tau_c_5, tau_e_5]);
    {% else %}
    mu[Omega] = mu0;
    nu[Omega] = nu0;
    {% endif %}

    // ------- MATERIAL PARAMETERS - ELECTRIC -------
    // Contact resistances for circuit equations
    R[Resistors_crossing] = 0.5 * <<dm.magnet.solve.general_parameters.crossing_coupling_resistance>>; // (Ohm) // Crossing contact resistance between strands, multiplication by 0.5 to account for oblique resistors which are not modelled separately (for better symmetry in results)
    R[Resistors_adjacent] = <<dm.magnet.solve.general_parameters.adjacent_coupling_resistance>>; // (Ohm) // Adjacent contact resistance between strands
    // Coating region resistivity
    rho[LinOmegaC] = <<dm.magnet.solve.general_parameters.rho_coating>>;  // (Ohm*m)
    // Strand resistivity
    rho[Strands] = <<dm.magnet.solve.general_parameters.rho_strands>>;  // (Ohm*m) when modelled as massive conductors

    {% if dm.magnet.solve.formulation_parameters.rohf %}
    // ROHF model for stranded strands
    Lint0 = mu0 / (4*Pi);
    // ROHF Model Parameters
    N_rohf = 5;
    // Weights (-)
    w_rohf_1 = 0.01; 
    w_rohf_2 = 0.05;
    w_rohf_3 = 0.1;
    w_rohf_4 = 0.5;
    w_rohf_5 = 2.0;
    // Irreversibility parameters (A)
    kappa_rohf_1 = 0;   // A, must be zero, this is MANDATORY!
    kappa_rohf_2 = 120; // A
    kappa_rohf_3 = 220; // A
    kappa_rohf_4 = 250; // A
    kappa_rohf_5 = 350; // A
    // Eddy current time constants (s)
    tau_e_rohf_1 = 1.5e-5; // s
    tau_e_rohf_2 = 2e-4; // s
    tau_e_rohf_3 = 2e-4; // s
    tau_e_rohf_4 = 2e-4; // s
    tau_e_rohf_5 = 2e-4; // s

    // --- Reversible current in dynamic case
    // $1: new current
    // $2: previous reversible + eddy current (G)
    // $3: irreversibility parameter
    G[] = (Norm[$1 - $2]#1 <= $3) ? $2 : $1 - $3 * ($1 - $2) / #1;
    dGdI[] = (Norm[$1 - $2] <= $3) ? 0.0 : 1.0;
    // $1: new current
    // $2: previous reversible current
    // $3: previous reversible + eddy current (G)
    // $4: irreversibility parameter
    // $5: time constant
    Irev_k[] = G[$1, $3, $4]#1 - $5 / ($DTime + $5) * (#1 - $2);
    dIrev_kdI[] = dGdI[$1, $3, $4]#1 -  $5 * #1 / ($DTime + $5);
    G_k[] = G[$1, $2, $3];
    // --- Main hysteresis law, written as the difference with respect to the linear case
    // $1: new total current
    // $(2*k): reversible current at previous time step for cell k
    // $(2*k+1): reversible current + eddy (G) at previous time step for cell k
    DeltaFluxhyst[] = Lint0 * (w_rohf_1 * Irev_k[$1, $2, $3, kappa_rohf_1, tau_e_rohf_1]
                             + w_rohf_2 * Irev_k[$1, $4, $5, kappa_rohf_2, tau_e_rohf_2]
                             + w_rohf_3 * Irev_k[$1, $6, $7, kappa_rohf_3, tau_e_rohf_3]
                             + w_rohf_4 * Irev_k[$1, $8, $9, kappa_rohf_4, tau_e_rohf_4]
                             + w_rohf_5 * Irev_k[$1, $10,$11,kappa_rohf_5, tau_e_rohf_5]
                             - 0*$1); // this contribution is removed in the formulation directly (and not here, hence the 0*)

    dDeltaFluxhystdI[] = Lint0 *  (w_rohf_1 * dIrev_kdI[$1, $2, $3, kappa_rohf_1, tau_e_rohf_1] //1.0
                                 + w_rohf_2 * dIrev_kdI[$1, $4, $5, kappa_rohf_2, tau_e_rohf_2]
                                 + w_rohf_3 * dIrev_kdI[$1, $6, $7, kappa_rohf_3, tau_e_rohf_3]
                                 + w_rohf_4 * dIrev_kdI[$1, $8, $9, kappa_rohf_4, tau_e_rohf_4]
                                 + w_rohf_5 * dIrev_kdI[$1, $10,$11,kappa_rohf_5, tau_e_rohf_5] 
                                 - 0*1); // this contribution is removed in the formulation directly (and not here, hence the 0*)

    DeltaFluxhyst_prev[] = Lint0 *(w_rohf_1 * $2
                                 + w_rohf_2 * $3
                                 + w_rohf_3 * $4
                                 + w_rohf_4 * $5
                                 + w_rohf_5 * $6 
                                 - 0*$1); // this contribution is removed in the formulation directly (and not here, hence the 0*)

    {% endif %}

    {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
    // --- Transport current - Resistive Voltage relationship in the strand
    // Power law for the superconducting filaments
    Ic[] = <<dm.magnet.solve.general_parameters.superconductor_Ic>>; // Critical current of the strand (A)
    n = <<dm.magnet.solve.general_parameters.superconductor_n_value>>; // Power law index (n)
    ec = 1e-4; // Voltage per unit length at critical current (V/m) 
    // Resistance (per unit length) of the conducting matrix
    R_matrix[] = <<dm.magnet.solve.general_parameters.matrix_resistance>>; // rho_matrix/area_matrix;
    // Simplified current sharing relationship (power law until derivative equals matrix resistance, then constant slope; continuous and continuously differentiable)
    I_threshold[] = (R_matrix[] * Ic[]^n / (n * ec))^(1/(n-1));
    V_resistance[] = (Abs[$1] < I_threshold[]) ? ec * (Abs[$1]/Ic[])^n * Sign[$1] : (R_matrix[] * (Abs[$1] - I_threshold[]) + ec * (I_threshold[]/Ic[])^n) * Sign[$1] ;
    dV_resistance_dI[] = (Abs[$1] < I_threshold[]) ? ec/Ic[] * n * (Abs[$1]/Ic[])^(n-1) : R_matrix[];
    {% endif %}

    {% if dm.magnet.solve.source_parameters.parallel_resistor %}
    {% if isinstance(dm.magnet.solve.source_parameters.parallel_resistor, float) %}
    R[ParallelResistor] = <<dm.magnet.solve.source_parameters.parallel_resistor>>; // Resistance of the parallel resistor
    {% else %}
    R[ParallelResistor] = 1.0; // Default resistance of 1 Ohm for the parallel resistor
    {% endif %}
    {% endif %}

    // ------- SOURCE PARAMETERS -------
    bmax = <<dm.magnet.solve.source_parameters.sine.field_amplitude>>; // Maximum applied magnetic induction [T]
    f = <<dm.magnet.solve.source_parameters.sine.frequency>>; // Frequency of applied field [Hz]
    Imax = <<dm.magnet.solve.source_parameters.sine.current_amplitude>>; // Maximum transport current [A]
    
    {% if dm.magnet.solve.frequency_domain_solver.frequency_sweep.run_sweep %}
    nbFreq = <<dm.magnet.solve.frequency_domain_solver.frequency_sweep.number_of_frequencies>>; // How many frequencies in the frequency domain?
    freq = LogSpace[Log10[<<dm.magnet.solve.frequency_domain_solver.frequency_sweep.start_frequency>>], Log10[<<dm.magnet.solve.frequency_domain_solver.frequency_sweep.end_frequency>>], nbFreq];
    {% endif %}

    // Direction and value of applied field
    {% if dm.magnet.solve.source_parameters.source_type == 'sine' %} // Sine wave source (potentially with DC component)
        time_multiplier = 1;

        ramp_duration = -0.05/f;

        constant_I_transport[] = ($Time < ramp_duration ) ? InterpolationLinear[$Time]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.sine.superimposed_DC.current_magnitude>>}]}  : <<dm.magnet.solve.source_parameters.sine.superimposed_DC.current_magnitude>>;
        I_transport[] = constant_I_transport[] + <<dm.magnet.solve.source_parameters.sine.current_amplitude>> * Sin[2*Pi*f * $Time];

        constant_field_direction[] = Vector[0., 1., 0.];
        directionApplied[] = Vector[Cos[<<dm.magnet.solve.source_parameters.sine.field_angle>>*Pi/180], Sin[<<dm.magnet.solve.source_parameters.sine.field_angle>>*Pi/180], 0.];

        constant_b[] = ($Time < ramp_duration ) ? InterpolationLinear[$Time]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>}]}  : <<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>;
        constant_b_prev[] = ($Time-$DTime < ramp_duration ) ? InterpolationLinear[$Time-$DTime]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>}]}  : <<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>;

        hsVal[] = nu0 * constant_b[] * constant_field_direction[] + nu0 * <<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * $Time] * directionApplied[];// * 200 * (X[] - 0.00625);
        hsVal_prev[] = nu0 * constant_b_prev[] * constant_field_direction[] + nu0 * <<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * ($Time-$DTime)] * directionApplied[];// * 200 * (X[] - 0.00625);

    {% elif dm.magnet.solve.source_parameters.source_type == 'piecewise' %}
        time_multiplier = <<dm.magnet.solve.source_parameters.piecewise.time_multiplier>>;
        applied_field_multiplier = <<dm.magnet.solve.source_parameters.piecewise.applied_field_multiplier>>;
        transport_current_multiplier = <<dm.magnet.solve.source_parameters.piecewise.transport_current_multiplier>>;
        directionApplied[] = Vector[Cos[<<dm.magnet.solve.source_parameters.piecewise.field_angle>>*Pi/180], Sin[<<dm.magnet.solve.source_parameters.piecewise.field_angle>>*Pi/180], 0.];

        {% if dm.magnet.solve.source_parameters.piecewise.source_csv_file %} // Source from CSV file
            timeList() = {<<ed['time']|join(', ')>>};
            bappList() = {<<ed['b']|join(', ')>>};
            IList() = {<<ed['I']|join(', ')>>};
            time_bapp_List() = ListAlt[timeList(), bappList()];
            time_I_List() = ListAlt[timeList(), IList()];

            hsVal[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{List[time_bapp_List()]} * directionApplied[];
            hsVal_prev[] = nu0 * applied_field_multiplier * InterpolationLinear[Max[0,($Time-$DTime)/time_multiplier]]{List[time_bapp_List()]} * directionApplied[];
            I_transport[] = transport_current_multiplier * InterpolationLinear[Max[0,($Time)/time_multiplier]]{List[time_I_List()]};
        
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

    {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
    // Excitation coils from file
    timeList() = {<<ed['time']|join(', ')>>};
    {% if dm.magnet.solve.source_parameters.excitation_coils.source_csv_file %}
    {% for i in range(1, 1+len(rm.powered.ExcitationCoils.vol.numbers)) %}
    I_<<i>>_list() = {<<ed['I'+str(i)]|join(', ')>>};
    time_I_<<i>>_List() = ListAlt[timeList(), I_<<i>>_list()];
    I_<<i>>[] = InterpolationLinear[Max[0,($Time)]]{List[time_I_<<i>>_List()]};
    {% endfor %}
    {% else %}
    I_1[] = + 2016 * (($Time < 2.0) ? 0.0 : 1.0) * Sin[2*Pi*f*$Time]; // For E-CLIQ test case in https://arxiv.org/abs/2510.24618
    I_2[] = - 2016 * (($Time < 2.0) ? 0.0 : 1.0) * Sin[2*Pi*f*$Time]; // For E-CLIQ test case in https://arxiv.org/abs/2510.24618
    {% endif %}
    {% endif %}

    // ------- NUMERICAL PARAMETERS -------
    timeStart = 0.; // Initial time [s]

    {% if dm.magnet.solve.source_parameters.source_type == 'sine'%}
        timeFinal = <<dm.magnet.solve.numerical_parameters.sine.number_of_periods_to_simulate>>/f; // Final time for source definition (s)
        dt = 1 / (f*<<dm.magnet.solve.numerical_parameters.sine.timesteps_per_period>>); // Time step (initial if adaptive) (s)
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
    
    iter_max = 200; // Maximum number of iterations (after which we exit the iterative loop)
    extrapolationOrder = 1; // Extrapolation order for predictor
    tol_energy = 1e-6; // Tolerance on the relative change of the power indicator
    writeInterval = dt; // Time interval to save the solution [s]

    // ------- Source Current -------
    Flag_save_hs = 0; // For debugging purposes, to see what are the computed source current and fields for stranded conductors
    Is0[] = Vector[0, 0, 1]; // source current of unit amplitude (A)

    // ------- SIMULATION NAME -------
    name = "txt_files";
    resDirectory = StrCat["./",name];
    infoResidualFile = StrCat[resDirectory,"/residual.txt"];
    outputPowerROHM = StrCat[resDirectory,"/power_ROHM.txt"]; // File updated during runtime
    outputPowerROHF = StrCat[resDirectory,"/power_ROHF.txt"];
    crashReportFile = StrCat[resDirectory,"/crash_report.txt"];

    {% if dm.magnet.solve.initial_conditions.init_from_pos_file %}
    h_from_file[] = VectorField[XYZ[]]; // After GmshRead[] in Resolution, this vector field contains the solution from a .pos file that can be accessed at any point XYZ[]
    {% endif %}

}

Constraint {
    { Name phi ;
        Case {
            {% if dm.magnet.solve.source_parameters.boundary_condition_type == 'Natural' %} // For natural boundary condition (in formulation)
            {Region ArbitraryPoints ; Value 0.0 ;} // Fix the magnetic potential to zero on the boundaries of the filaments and the outer matrix boundary
            {% elif dm.magnet.solve.source_parameters.boundary_condition_type == 'Essential' %}
            {Region BndAir ; Type Assign ; Value XYZ[]*directionApplied[] ; TimeFunction hsVal[] * directionApplied[] ;} // Essential boundary condition (not compatible with transport current)
            {% endif %}
            {% if dm.magnet.solve.initial_conditions.init_from_pos_file %}
            {Region Omega ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }
    { Name Current ;
        Case {
            {% if dm.magnet.solve.frequency_domain_solver.enable %}
            {Region CoatingCut ; Value Complex[Imax,0];} // Contraint for the total transport current
            {% else %}
            {% if not dm.magnet.solve.source_parameters.parallel_resistor %}
            {Region CoatingCut ; Type Assign ; Value 1.0 ; TimeFunction I_transport[] ;} // Contraint for the total transport current
            {% endif %}
            {% endif %}     
            {% if dm.magnet.solve.initial_conditions.init_from_pos_file %}
            {Region Cuts ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
            // {Region Cuts ; Type Assign ; Value 0. ;} // for debugging (or to model fully uncoupled filaments without transport current)
        }
    }
    { Name Voltage ; Case {} } // Empty to avoid warnings
    { Name Voltage_s ; Case {} } // Empty to avoid warnings
    { Name Current_Cir ; 
        Case {
            // { Region Resistors ; Value 0.0 ; }
            // { Region Strands ; Value 0.0 ; }
        } 
    }
    { Name Voltage_Cir ; Case {} } // Empty to avoid warnings
    {% if dm.magnet.solve.source_parameters.parallel_resistor %}
    { Name Current_Cir_transport ; 
        Case {
            {Region CurrentSource ; Value 1.0 ; TimeFunction I_transport[] ;}
        } 
    } // Empty to avoid warnings
    { Name Voltage_Cir_transport ; Case {} } // Empty to avoid warnings
    {% endif %}
    // This is the key constraint for coupling global quantities: it contains the links between the filaments
    {Name ElectricalCircuit ; Type Network ;
        Case circuit {
            // 1) Branching between strands accounting for transposition
            {% for i in range(1, len(rm.powered.Strands.cochain.numbers)+1) %}
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            {Region Strand_<<i>> ; Branch { <<i>>, <<i % len(rm.powered.Strands.cochain.numbers) + 1 >> } ;}
            {% else %}
            {Region Cut_<<i>> ; Branch { <<i>>, <<i % len(rm.powered.Strands.cochain.numbers) + 1 >> } ;}
            {% endif %}
            {% endfor %}
            // 2) Adding crossing contact resistance connections 
            {% for i in range(1, int(len(rm.powered.Strands.cochain.numbers)/2)) %}
            {Region R_crossing_<<i>> ; Branch { <<i+1>>, <<len(rm.powered.Strands.cochain.numbers) - (i-1) >> } ;}
            {% endfor %}
            // // 3) Adding oblique contact resistances (not done anymore; instead, the crossing resistance is twice smaller to account for oblique connections)
            // {% for i in range(1,len(rm.powered.Strands.cochain.numbers)+1) %}
            // {% if i <= int(len(rm.powered.Strands.cochain.numbers)/2) %}
            // {Region R_crossing_oblique_<<i>> ; Branch { <<i>>, <<len(rm.powered.Strands.cochain.numbers) - (i-1) >> } ;}
            // {%else%}
            // {Region R_crossing_oblique_<<i>> ; Branch { <<i%len(rm.powered.Strands.cochain.numbers)+1>>, <<len(rm.powered.Strands.cochain.numbers)+2 -i >> } ;}
            // {%endif%}
            // {% endfor %}
            // 4) Adding adjacent contact resistance connections
            {% for i in range(1, len(rm.powered.Strands.cochain.numbers)+1) %}
            {Region R_adjacent_<<i>> ; Branch { <<i>>, <<i % len(rm.powered.Strands.cochain.numbers) + 1 >> } ;}
            {% endfor %}
        }
    }
    {% if dm.magnet.solve.source_parameters.parallel_resistor %}
    {Name ElectricalCircuit_transport ; Type Network ;
        Case circuit1 {
            {Region CoatingCut ; Branch { 2, 1 } ;}
            {Region CurrentSource ; Branch { 1, 2 } ;}
            {Region ParallelResistor ; Branch { 1, 2 } ;}
        }
    }
    {% endif %}
    { Name h ; Type Assign ;
        Case {
            {% if dm.magnet.solve.initial_conditions.init_from_pos_file %}
            {Region OmegaC ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }
    {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
    // Gauging condition for the source field
    {% for i in range(0, len(rm.powered.Strands.vol.numbers)) %}
    { Name GaugeCondition_hs_<<i+1>> ; Type Assign ;
        Case {
            { Region Strand_<<i+1>> ; SubRegion StrandBnd_<<i+1>> ; Value 0. ; }
        }
    }
    {% endfor %}
    // Constraint for the source field, such that it is associated with a unit current (basis function)
    { Name Current_hs ; Type Assign ;
        Case {
            { Region Cuts; Value 1.0;}
        }
    }
    { Name Current_s ; Type Assign ;
        Case {
            // { Region OmegaC_stranded; Value 1.0; TimeFunction Sin[2*Pi*f * $Time];}
        }
    }
    {% endif %}
    {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
    {% for i in range(0, len(rm.powered.ExcitationCoils.vol.numbers)) %}
    { Name GaugeCondition_hs_coil_<<i+1>> ; Type Assign ;
        Case {
            { Region Coil_<<i+1>> ; SubRegion CoilBnd_<<i+1>> ; Value 0. ; }
        }
    }
    {% endfor %}
    { Name Current_hs_coil ; Type Assign ;
        Case {
            { Region Cuts; Value 1.0;}
        }
    }
    { Name Current_coil ; Type Assign ;
        Case {
            {% for i in range(0, len(rm.powered.ExcitationCoils.vol.numbers)) %}
            { Region Coil_<<i+1>>; Value 1.0; TimeFunction I_<<i+1>>[];}
            {% endfor %}
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
    // For efficient assembly in hysteretic elements, integration of {b} and bhyst[{h}] which are constant per element AND mostly to avoid systematic numerical integration error.
    { Name Int_b ;
        Case {
            { Type Gauss ;
                Case {
                    { GeoElement Triangle ; NumberOfPoints 1 ; }
                    { GeoElement Quadrangle ; NumberOfPoints 1 ; }
                }
            }
        }
    }
}

{% if dm.magnet.solve.formulation_parameters.stranded_strands %}
For i In {1 : <<len(rm.powered.Strands.vol.numbers)>>}
    // Source field definition (must be done above the rest)
    FunctionSpace {        
        // Function space for the source field (defined during pre-resolution, and then included as a sub-space in the main h_space)
        { Name hs_space~{i}; Type Form1;
            BasisFunction {
                { Name psie; NameOfCoef he; Function BF_Edge;
                    Support Strand~{i}; Entity EdgesOf[All, Not StrandBnd~{i}]; }
                { Name sc; NameOfCoef Ii; Function BF_GroupOfEdges;
                    Support Omega; Entity GroupsOfEdgesOf[Cut~{i}]; }
            }
            Constraint {
                { NameOfCoef he; EntityType EdgesOfTreeIn; EntitySubType StartingOn;
                    NameOfConstraint GaugeCondition_hs~{i}; }
                { NameOfCoef Ii ; EntityType GroupsOfEdgesOf ; NameOfConstraint Current_hs ; }
            }
        }
    }
    Formulation{
        // Formulation for source currents in strands
        { Name js_to_hs~{i} ; Type FemEquation ;
            Quantity {
                { Name hs ; Type Local  ; NameOfSpace hs_space~{i} ; }
            }
            Equation {
                Galerkin { [  Dof{d hs}, {d hs} ] ;
                    In Strand~{i} ; Jacobian Vol ; Integration Int ; }
                Galerkin { [ - Is0[]/SurfaceArea[], {d hs} ] ;
                    In Strand~{i} ; Jacobian Vol ; Integration Int ; }
            }
        }
    }
    Resolution{
        { Name js_to_hs~{i} ;
            System {
                { Name Sys_Mag ; NameOfFormulation js_to_hs~{i} ; }
            }
            Operation {
                Generate Sys_Mag ; Solve Sys_Mag ;
                If(Flag_save_hs == 1) PostOperation[js_to_hs~{i}] ; SaveSolution Sys_Mag ; EndIf
            }
        }
    }
    PostProcessing{
        { Name js_to_hs~{i} ; NameOfFormulation js_to_hs~{i} ;
            PostQuantity {
                { Name hs  ; Value { Term { [ {hs} ] ; Jacobian Vol ;
                    In Omega ; } } }
                { Name js  ; Value { Term { [ {d hs} ] ; Jacobian Vol ;
                    In Omega ; } } }
                { Name js0 ; Value { Term { [ Is0[]/SurfaceArea[] ] ;
                    In Omega ; Jacobian Vol ; } } }
            }
        }
    }
    PostOperation{
        { Name js_to_hs~{i}; NameOfPostProcessing js_to_hs~{i};
            Operation{
                Print[ hs, OnElementsOf Omega , File Sprintf("hs_%g.pos", i), Name "hs [A/m]" ];
                Print[ js, OnElementsOf Strand~{i} , File Sprintf("js_%g.pos", i), Name "js [A/m2]" ];
                Print[ js0, OnElementsOf Strand~{i} , File Sprintf("js0_%g.pos", i), Name "js0 [A/m2]" ];
            }
        }
    }
EndFor
{% endif %}
{% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
For i In {1 : <<len(rm.powered.ExcitationCoils.vol.numbers)>>}
    FunctionSpace {        
        // Function space for the source field (defined during pre-resolution, and then included as a sub-space in the main h_space)
        { Name hs_coil_space~{i}; Type Form1;
            BasisFunction {
                { Name psie; NameOfCoef he; Function BF_Edge;
                    Support Coil~{i}; Entity EdgesOf[All, Not CoilBnd~{i}]; }
                { Name sc; NameOfCoef Ii; Function BF_GroupOfEdges;
                    Support Omega; Entity GroupsOfEdgesOf[CutCoil~{i}]; }
            }
            Constraint {
                { NameOfCoef he; EntityType EdgesOfTreeIn; EntitySubType StartingOn;
                    NameOfConstraint GaugeCondition_hs_coil~{i}; }
                { NameOfCoef Ii ; EntityType GroupsOfEdgesOf ; NameOfConstraint Current_hs_coil ; }
            }
        } 
    }
    Formulation{
        // Formulation for source currents in coils
        { Name js_to_hs_coil~{i} ; Type FemEquation ;
            Quantity {
                { Name hs ; Type Local  ; NameOfSpace hs_coil_space~{i} ; }
            }
            Equation {
                Galerkin { [  Dof{d hs}, {d hs} ] ;
                    In Coil~{i} ; Jacobian Vol ; Integration Int ; }
                Galerkin { [ - Is0[]/SurfaceArea[], {d hs} ] ;
                    In Coil~{i} ; Jacobian Vol ; Integration Int ; }
            }
        }
    }
    Resolution{
        { Name js_to_hs_coil~{i} ;
            System {
                { Name Sys_Mag ; NameOfFormulation js_to_hs_coil~{i} ; }
            }
            Operation {
                Generate Sys_Mag ; Solve Sys_Mag ;
            }
        }
    }
EndFor
{% endif %}

FunctionSpace {
    // Function space for magnetic field h in h-conform formulation. Main field for the magnetodynamic problem.
    //  h = sum phi_n * grad(psi_n)     (nodes in Omega_CC with boundary)
    //      + sum h_e * psi_e           (edges in Omega_C)
    //      + sum I_i * c_i             (cuts, global basis functions for net current intensity)
    //      + [TBC]
    { Name h_space; Type Form1;
        BasisFunction {
            { Name gradpsin; NameOfCoef phin; Function BF_GradNode;
                Support OmegaCC_AndBnd; Entity NodesOf[OmegaCC]; } // Extend support to boundary for surface integration (e.g. useful for weak B.C.)
            { Name gradpsin; NameOfCoef phin2; Function BF_GroupOfEdges;
                Support OmegaC; Entity GroupsOfEdgesOnNodesOf[BndOmegaC]; } // To treat properly the Omega_CC-Omega_C boundary
            { Name psie; NameOfCoef he; Function BF_Edge;
                Support OmegaC_AndBnd; Entity EdgesOf[All, Not BndOmegaC]; }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            { Name sc; NameOfCoef Ii; Function BF_GroupOfEdges;
                Support Omega; Entity GroupsOfEdgesOf[CoatingCut]; } // The region Cuts contains the union of all the relevant cuts (cohomology basis function support)
            { Name sb ; NameOfCoef Is ;  // Global Basis Function
                Function BF_Global { 
                    Quantity hs ;
                    Formulation js_to_hs {<<len(rm.powered.Strands.vol.numbers)>>} ;
                    Group OmegaC_stranded ; Resolution js_to_hs {<<len(rm.powered.Strands.vol.numbers)>>} ;
                } ;
                Support OmegaC_and_stranded ; Entity Global [OmegaC_stranded] ; }
            {% else %}
            { Name sc; NameOfCoef Ii; Function BF_GroupOfEdges;
                Support Omega; Entity GroupsOfEdgesOf[CoatingCut, StrandCuts]; } // The region Cuts contains the union of all the relevant cuts (cohomology basis function support)
            {% endif %}
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            { Name sb_coil ; NameOfCoef Ic ;  // Global Basis Function
                Function BF_Global { 
                    Quantity hs ;
                    Formulation js_to_hs_coil {<<len(rm.powered.ExcitationCoils.vol.numbers)>>} ;
                    Group Coils ; Resolution js_to_hs_coil {<<len(rm.powered.ExcitationCoils.vol.numbers)>>} ;
                } ;
                Support Omega ; Entity Global [Coils] ; }
            {% endif %}
        }
        {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
        SubSpace{
            { Name hs ; NameOfBasisFunction sb; }
        }
        {% endif %}
        GlobalQuantity {
            { Name I ; Type AliasOf        ; NameOfCoef Ii ; }
            { Name V ; Type AssociatedWith ; NameOfCoef Ii ; }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            { Name Is ; Type AliasOf        ; NameOfCoef Is ; }
            { Name Vs ; Type AssociatedWith ; NameOfCoef Is ; }
            {% endif %}
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            { Name Ic ; Type AliasOf        ; NameOfCoef Ic ; }
            { Name Vc ; Type AssociatedWith ; NameOfCoef Ic ; }
            {% endif %}
        }
        Constraint {
            { NameOfCoef he; EntityType EdgesOf; NameOfConstraint h; }
            { NameOfCoef phin; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef phin2; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef Ii ;
                EntityType GroupsOfEdgesOf ; NameOfConstraint Current ; }
            { NameOfCoef V ;
                EntityType GroupsOfNodesOf ; NameOfConstraint Voltage ; }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            { NameOfCoef Is ;
                EntityType Region ; NameOfConstraint Current_s ; }
            { NameOfCoef Vs ;
                EntityType Region ; NameOfConstraint Voltage_s ; }
            {% endif %}
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            { NameOfCoef Ic ;
                EntityType Region ; NameOfConstraint Current_coil ; }
            { NameOfCoef Vc ;
                EntityType Region ; NameOfConstraint Voltage_coil ; }
            {% endif %}
        }
    }
    // Function space for the circuit domain
    { Name ElectricalCircuit; Type Scalar;
        BasisFunction {
            { Name sn; NameOfCoef Ir; Function BF_Region;
                Support Resistors; Entity Resistors; }
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
    {% if dm.magnet.solve.source_parameters.parallel_resistor %}
    // Function space for the circuit domain
    { Name ElectricalCircuit_transport; Type Scalar;
        BasisFunction {
            { Name sn; NameOfCoef Icoef; Function BF_Region;
                Support PoweringCircuit; Entity PoweringCircuit; }
        }
        GlobalQuantity {
            { Name Ip ; Type AliasOf        ; NameOfCoef Icoef ; }
            { Name Vp ; Type AssociatedWith ; NameOfCoef Icoef ; }
        }
        Constraint {
            { NameOfCoef Ip ; EntityType Region ; NameOfConstraint Current_Cir_transport ; }
            { NameOfCoef Vp ; EntityType Region ; NameOfConstraint Voltage_Cir_transport ; }
        }
    }
    {% endif %}
    {% if dm.magnet.solve.formulation_parameters.rohf and dm.magnet.solve.formulation_parameters.stranded_strands %}
    // Function space for the reversible current in stranded strands domains modelled with ROHF
    For k In {1:N_rohf}
        { Name IrevStrands~{k}; Type Scalar;
            BasisFunction {
                { Name srevstrand; NameOfCoef Irevstrand; Function BF_Region;
                    Support Strands; Entity Strands; }
            }
            GlobalQuantity {
                { Name Irev ; Type AliasOf ; NameOfCoef Irevstrand ; }
            }
        }
        { Name G~{k}; Type Scalar;
            BasisFunction {
                { Name sGtrand; NameOfCoef Gstrand; Function BF_Region;
                    Support Strands; Entity Strands; }
            }
            GlobalQuantity {
                { Name G ; Type AliasOf ; NameOfCoef Gstrand ; }
            }
        }
    EndFor
    {% endif %}
    {% if dm.magnet.solve.formulation_parameters.rohm %}
    // Function space for b from ROHM. Element-wise constant functions
    { Name b_space ; Type Vector;
        BasisFunction {
            { Name sex ; NameOfCoef aex ; Function BF_VolumeX ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
            { Name sey ; NameOfCoef aey ; Function BF_VolumeY ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
        }
    }
    // Function space for internal state variable with ROHM (h_rev for each cell). One space per cell.
    For k In {1:N}
        { Name hrev~{k} ; Type Form1;
            BasisFunction {
                { Name psie; NameOfCoef he; Function BF_Edge;
                    Support MagnHystDomain; Entity EdgesOf[All]; }
                // { Name sex ; NameOfCoef aex ; Function BF_VolumeX ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
                // { Name sey ; NameOfCoef aey ; Function BF_VolumeY ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
            }
        }
        // We can also recompute the 'g~{k}' below, instead of saving them. To be seen which approach is the most efficient.
        { Name g~{k} ; Type Form1;
            BasisFunction {
                { Name psie; NameOfCoef he; Function BF_Edge;
                    Support MagnHystDomain; Entity EdgesOf[All]; }
                // { Name vex ; NameOfCoef bex ; Function BF_VolumeX ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
                // { Name vey ; NameOfCoef bey ; Function BF_VolumeY ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
            }
        }
    EndFor
    {% endif %}
}

Formulation{
    // h-formulation
    { Name MagDyn_hphi; Type FemEquation;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
            { Name hp; Type Local; NameOfSpace h_space; }
            { Name I; Type Global; NameOfSpace h_space[I]; }
            { Name V; Type Global; NameOfSpace h_space[V]; }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            { Name Is ; Type Global; NameOfSpace h_space[Is]; }
            { Name Vs ; Type Global; NameOfSpace h_space[Vs]; }
            {% if dm.magnet.solve.formulation_parameters.rohf %}
            For k In {1:N_rohf}
                { Name Irev~{k} ; Type Global; NameOfSpace IrevStrands~{k}[Irev]; }
                { Name G~{k} ; Type Global; NameOfSpace G~{k}[G]; }
            EndFor
            { Name hs; Type Local; NameOfSpace h_space[hs]; }
            {% endif %}
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            { Name b; Type Local; NameOfSpace b_space; }
            For k In {1:N}
                { Name hrev~{k}  ; Type Local ; NameOfSpace hrev~{k};}
                { Name g~{k}  ; Type Local ; NameOfSpace g~{k};}
            EndFor
            {% endif %}
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            { Name Ic ; Type Global; NameOfSpace h_space[Ic]; }
            { Name Vc ; Type Global; NameOfSpace h_space[Vc]; }
            {% endif %}
            { Name Iz; Type Global; NameOfSpace ElectricalCircuit[Iz]; }
            { Name Vz; Type Global; NameOfSpace ElectricalCircuit[Vz]; }
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            { Name Ip ; Type Global; NameOfSpace ElectricalCircuit_transport[Ip]; }
            { Name Vp ; Type Global; NameOfSpace ElectricalCircuit_transport[Vp]; }
            {% endif %}
        }
        Equation {
            // --- Axial currents problem ---
            // Time derivative of b (NonMagnDomain)
            Galerkin { [ ell* mu[] * Dof{h} / $DTime , {h} ];
                In MagnLinDomain; Integration Int; Jacobian Vol;  }
            Galerkin { [ -ell*mu[] * {h}[1] / $DTime , {h} ];
                In MagnLinDomain; Integration Int; Jacobian Vol;  }
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            Galerkin { [ ell * bhyst[{h}, {hrev_1}[1], {g_1}[1], {hrev_2}[1], {g_2}[1], {hrev_3}[1], {g_3}[1], {hrev_4}[1], {g_4}[1], {hrev_5}[1], {g_5}[1], Norm[{b}]] / $DTime , {h} ];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ ell * dbhystdh[{h}, {hrev_1}[1], {g_1}[1], {hrev_2}[1], {g_2}[1], {hrev_3}[1], {g_3}[1], {hrev_4}[1], {g_4}[1], {hrev_5}[1], {g_5}[1], Norm[{b}]] * Dof{h} / $DTime , {hp}];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ - ell * dbhystdh[{h}, {hrev_1}[1], {g_1}[1], {hrev_2}[1], {g_2}[1], {hrev_3}[1], {g_3}[1], {hrev_4}[1], {g_4}[1], {hrev_5}[1], {g_5}[1], Norm[{b}]] * {h}  / $DTime , {hp}];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ - ell * {b}[1] / $DTime , {h} ];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }

            {% if dm.magnet.solve.formulation_parameters.rohf and dm.magnet.solve.formulation_parameters.stranded_strands%}
            // Removing the contribution from {hs} inside the strands, such that the linear internal flux contribution is not counted twice.
            Galerkin { [ - ell * bhyst[{h}, {hrev_1}[1], {g_1}[1], {hrev_2}[1], {g_2}[1], {hrev_3}[1], {g_3}[1], {hrev_4}[1], {g_4}[1], {hrev_5}[1], {g_5}[1], Norm[{b}]] / $DTime , {hs} ];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ - ell * dbhystdh[{h}, {hrev_1}[1], {g_1}[1], {hrev_2}[1], {g_2}[1], {hrev_3}[1], {g_3}[1], {hrev_4}[1], {g_4}[1], {hrev_5}[1], {g_5}[1], Norm[{b}]] * Dof{h} / $DTime , {hs}];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ + ell * dbhystdh[{h}, {hrev_1}[1], {g_1}[1], {hrev_2}[1], {g_2}[1], {hrev_3}[1], {g_3}[1], {hrev_4}[1], {g_4}[1], {hrev_5}[1], {g_5}[1], Norm[{b}]] * {h}  / $DTime , {hs}];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ + ell * {b}[1] / $DTime , {hs} ];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            {% endif %}
            {% endif %}
            // Induced current (linear OmegaC). Nothing with integrals in the strands, they are handled by the circuit equations
            Galerkin { [ ell * rho[mu0*Norm[{h}]] * Dof{d h} , {d h} ];
                In OmegaC; Integration Int; Jacobian Vol;  }
            // Natural boundary condition for normal flux density (useful when transport current is an essential condition)
            {% if dm.magnet.solve.source_parameters.boundary_condition_type == 'Natural' %}
            Galerkin { [ -ell * dbsdt[] * Normal[] , {dInv h} ];
                In BndAir; Integration Int; Jacobian Sur;  }
            {% endif %}
            // Global term
            GlobalTerm { [ Dof{V} , {I} ] ; In CoatingCut ; }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            GlobalTerm { [ Dof{Vs} , {Is} ] ; In Strands ; }
            {% else %}
            GlobalTerm { [ Dof{V} , {I} ] ; In StrandCuts ; }
            {% endif %}
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            GlobalTerm { [ Dof{Vc} , {Ic} ] ; In CoilCuts ; }
            {% endif %}
            // Resistance equation for the crossing/adjacent contact resistance
            GlobalTerm{ [ Dof{Vz} , {Iz} ]; In Resistors; }
            GlobalTerm{ [ R[] * Dof{Iz} , {Iz} ]; In Resistors; }
            {% if dm.magnet.solve.formulation_parameters.rohf and dm.magnet.solve.formulation_parameters.stranded_strands%}
            // ROHF model for the current flowing in the strands
            GlobalTerm{ [ + ell * DeltaFluxhyst[   {Is}, {Irev_1}[1], {G_1}[1], {Irev_2}[1], {G_2}[1], {Irev_3}[1], {G_3}[1], {Irev_4}[1], {G_4}[1], {Irev_5}[1], {G_5}[1]]/$DTime , {Is} ]; In Strands; }
            GlobalTerm{ [ + ell * dDeltaFluxhystdI[{Is}, {Irev_1}[1], {G_1}[1], {Irev_2}[1], {G_2}[1], {Irev_3}[1], {G_3}[1], {Irev_4}[1], {G_4}[1], {Irev_5}[1], {G_5}[1]]/$DTime * Dof{Is} , {Is} ]; In Strands; }
            GlobalTerm{ [ - ell * dDeltaFluxhystdI[{Is}, {Irev_1}[1], {G_1}[1], {Irev_2}[1], {G_2}[1], {Irev_3}[1], {G_3}[1], {Irev_4}[1], {G_4}[1], {Irev_5}[1], {G_5}[1]]/$DTime * {Is} , {Is} ]; In Strands; }
            GlobalTerm{ [ - ell * DeltaFluxhyst_prev[{Is}[1], {Irev_1}[1], {Irev_2}[1], {Irev_3}[1], {Irev_4}[1], {Irev_5}[1]]/$DTime , {Is} ]; In Strands; }

            GlobalTerm{ [ + ell * V_resistance[{Is}] , {Is} ]; In Strands; }
            GlobalTerm{ [ + ell * dV_resistance_dI[{Is}] * Dof{Is} , {Is} ]; In Strands; }
            GlobalTerm{ [ - ell * dV_resistance_dI[{Is}] * {Is} , {Is} ]; In Strands; }
            {% else %}
            // GlobalTerm{ [ 1e-7 * ell * Dof{Is} , {Is} ]; In Strands; } // For tests only (resistive stranded strand)
            {% endif %}
            // Circuit network for the CATI method
            GlobalEquation {
                Type Network ; NameOfConstraint ElectricalCircuit ;
                {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
                { Node {Is};  Loop {Vs};  Equation {Vs};  In Strands ; }
                {% else %}
                { Node {I};  Loop {V};  Equation {V};  In Cuts ; }
                {% endif %}
                { Node {Iz}; Loop {Vz}; Equation {Vz}; In Resistors; }
          	}
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            GlobalTerm{ [ Dof{Vp} , {Ip} ]; In ParallelResistor; }
            GlobalTerm{ [ R[]*ell * Dof{Ip} , {Ip} ]; In ParallelResistor; }
            // Circuit network for transport current and voltage
            GlobalEquation {
                Type Network ; NameOfConstraint ElectricalCircuit_transport ;
                { Node {I};  Loop {V};  Equation {V};  In CoatingCut ; }
                { Node {Ip}; Loop {Vp}; Equation {Vp}; In PoweringCircuit; }
          	}
            {% endif %}
        }
    }
    // Frequency domain formulation
    { Name MagDyn_hphi_freq; Type FemEquation;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
            { Name hp; Type Local; NameOfSpace h_space; }
            { Name I; Type Global; NameOfSpace h_space[I]; }
            { Name V; Type Global; NameOfSpace h_space[V]; }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            { Name Is ; Type Global; NameOfSpace h_space[Is]; }
            { Name Vs ; Type Global; NameOfSpace h_space[Vs]; }
            {% endif %}
            { Name Iz; Type Global; NameOfSpace ElectricalCircuit[Iz]; }
            { Name Vz; Type Global; NameOfSpace ElectricalCircuit[Vz]; }
        }
        Equation {
            // --- OOP problem ---
            // Time derivative of b (NonMagnDomain)
            Galerkin { DtDof[ ell* mu[] * Dof{h}, {h} ];
                In Omega; Integration Int; Jacobian Vol;  }
            // Induced current (linear OmegaC; nonlinear materials not allowed in the frequency domain)
            Galerkin { [ ell*rho[] * Dof{d h} , {d h} ];
                In OmegaC; Integration Int; Jacobian Vol;  }
            // Galerkin { [ ell*rho[] * Dof{d h} , {d h} ];
            //     In OmegaC_stranded; Integration Int; Jacobian Vol;  }
            // Natural boundary condition for normal flux density (useful when transport current is an essential condition)
            {% if dm.magnet.solve.source_parameters.boundary_condition_type == 'Natural' %}
            Galerkin { [ - ell* Complex[0, 2*Pi*$f*bmax]*Vector[Cos[<<dm.magnet.solve.source_parameters.sine.field_angle>>*Pi/180], Sin[<<dm.magnet.solve.source_parameters.sine.field_angle>>*Pi/180], 0.] * Normal[] , {dInv h} ]; 
                In BndAir; Integration Int; Jacobian Sur;  }
            {% endif %}
            // Global term
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            GlobalTerm { [ Dof{V} , {I} ] ; In CoatingCut ; }
            GlobalTerm { [ Dof{Vs} , {Is} ] ; In Strands ; }
            {% else %}
            GlobalTerm { [ Dof{V} , {I} ] ; In Cuts ; }
            {% endif %}
            // Resistance equation for the crossing contact resistances
            GlobalTerm{ [ Dof{Vz} , {Iz} ];  In Resistors; }
            GlobalTerm{ [ R[] * Dof{Iz} , {Iz} ];  In Resistors; }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            // Resistance model for the current flowing in the strands. The ROHF model cannot be solved in the frequency domain. 
            // GlobalTerm{ [ ell * 1e-4 * Dof{Is} , {Is} ];  In Strands; } // Just for testing. 
            {% endif %}
            // Circuit network
            GlobalEquation {
                Type Network ; NameOfConstraint ElectricalCircuit ;
                {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
                { Node {Is};  Loop {Vs};  Equation {Vs};  In Strands ; }
                {% else %}
                { Node {I};  Loop {V};  Equation {V};  In Cuts ; }
                {% endif %}
                { Node {Iz}; Loop {Vz}; Equation {Vz}; In Resistors; }
          	}
        }
    }
    {% if dm.magnet.solve.initial_conditions.init_from_pos_file %}
    // Projection formulation for initial condition
    { Name Projection_h_to_h; Type FemEquation;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
        }
        Equation{
            // For the current formulation, it seems to be accurate enough to project the field directly (and not its curl as an intermediate to reconstruct it).
            // Validity of this to be checked again if we go to different meshes between the initial condition and the following simulation.
            Galerkin { [  Dof{h}, {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
            Galerkin { [ - h_from_file[], {h} ] ;
                In Omega ; Jacobian Vol ; Integration Int ; }
        }
    }
    {% endif %}
    {% if dm.magnet.solve.formulation_parameters.rohm %}
    // Update of b in hysteresis model
    { Name Update_b; Type FemEquation ;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
            { Name b ; Type Local ; NameOfSpace b_space ; }
            For k In {1:N}
                { Name hrev~{k}  ; Type Local ; NameOfSpace hrev~{k};}
                { Name g~{k}  ; Type Local ; NameOfSpace g~{k};}
            EndFor
        }
        Equation {
            Galerkin { [ Dof{b} , {b} ];
                In MagnHystDomain; Jacobian Vol; Integration Int; }
            Galerkin { [ - bhyst[{h}, {hrev_1}[1], {g_1}[1], {hrev_2}[1], {g_2}[1], {hrev_3}[1], {g_3}[1], {hrev_4}[1], {g_4}[1], {hrev_5}[1], {g_5}[1], Norm[{b}]] , {b} ];
                In MagnHystDomain; Jacobian Vol; Integration Int; }
        }
    }
    // Update of internal variables
    For k In {1:N}
        { Name Update_hrev~{k} ; Type FemEquation ;
            Quantity {
                { Name h; Type Local; NameOfSpace h_space; }
                { Name b ; Type Local ; NameOfSpace b_space ; }
                { Name hrev~{k}  ; Type Local ; NameOfSpace hrev~{k};}
                { Name g~{k}  ; Type Local ; NameOfSpace g~{k};}
            }
            Equation {
                Galerkin { [ Dof{hrev~{k}}, {hrev~{k}} ];
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ - hrev_k[{h}, {hrev~{k}}[1], {g~{k}}[1], w~{k}, f_kappa[Norm[{b}]]*kappa~{k}, f_chi[Norm[{b}]]*chi~{k}, tau_c~{k}, tau_e~{k}], {hrev~{k}} ] ;
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ Dof{g~{k}}, {g~{k}} ];
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ - g_k[{h}, {hrev~{k}}[1], {g~{k}}[1], f_kappa[Norm[{b}]]*kappa~{k}], {g~{k}} ] ;
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
            }
        }
    EndFor
    {% endif %}
    {% if dm.magnet.solve.formulation_parameters.stranded_strands and dm.magnet.solve.formulation_parameters.rohf%}
    For k In {1:N_rohf}
        { Name Update_Irev~{k} ; Type FemEquation ;
            Quantity {
                { Name Is ;         Type Global; NameOfSpace h_space[Is]; }
                { Name Irev~{k} ;   Type Global; NameOfSpace IrevStrands~{k}[Irev]; }
                { Name G~{k} ;      Type Global; NameOfSpace G~{k}[G]; }
            }
            Equation {
                GlobalTerm{ [ Dof{Irev~{k}}, {Irev~{k}} ];  In Strands; }
                GlobalTerm{ [ - Irev_k[{Is}, {Irev~{k}}[1], {G~{k}}[1], kappa_rohf~{k}, tau_e_rohf~{k}], {Irev~{k}} ];  In Strands; }
                GlobalTerm{ [ Dof{G~{k}}, {G~{k}} ];  In Strands; }
                GlobalTerm{ [ - G_k[{Is}, {G~{k}}[1], kappa_rohf~{k}], {G~{k}} ];  In Strands; }
            }
        }
    EndFor
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
    Print[{$iter, $res, $res / $res0, $indicTotalLoss},
        Format "%g %14.12e %14.12e %14.12e", File infoResidualFile];
    // ----- Enter the iterative loop (hand-made) -----
    While[$convCrit > 1 && $res / $res0 <= 1e10 && $iter < iter_max]{
        Solve[A]; Evaluate[ $syscount = $syscount + 1 ];
        {% if dm.magnet.solve.formulation_parameters.rohm %}
        Generate[B]; Solve[B]; // update {b} so that the field-dependent parameter is updated for the convergence criterion
        {% endif %}
        Generate[A]; GetResidual[A, $res];
        Evaluate[ $iter = $iter + 1 ];
        Evaluate[ $indicTotalLossOld = $indicTotalLoss];
        PostOperation[MagDyn_energy];
        Print[{$iter, $res, $res / $res0, $indicTotalLoss},
            Format "%g %14.12e %14.12e %14.12e", File infoResidualFile]; // Here, the loss is not the real one, as the memory fields used to compute it are not updated yet (for efficiency). To be possibly modified if this gets annoying.
        // Evaluate the convergence indicator
        Evaluate[ $relChangeACLoss = Abs[($indicTotalLossOld - $indicTotalLoss)/((Abs[$indicTotalLossOld]>1e-7 || $iter < 10) ? $indicTotalLossOld:1e-7)] ];
        Evaluate[ $convCrit = $relChangeACLoss/tol_energy];
    }
Return

Resolution {
    { Name MagDyn;
        System {
            {Name A; NameOfFormulation MagDyn_hphi;}
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            {Name B; NameOfFormulation Update_b; }
            For k In {1:N}
                {Name CELL~{k}; NameOfFormulation Update_hrev~{k}; }
            EndFor
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.stranded_strands and dm.magnet.solve.formulation_parameters.rohf%}
            For k In {1:N_rohf}
                {Name CELL_ROHF~{k}; NameOfFormulation Update_Irev~{k}; }
            EndFor
            {% endif %}
        }
        Operation {
            // Initialize directories
            CreateDirectory[resDirectory];
            DeleteFile[outputPowerROHM];
            DeleteFile[outputPowerROHF];
            DeleteFile[infoResidualFile];
            // Initialize the solution (initial condition)
            SetTime[ timeStart ];
            SetDTime[ dt ];
            SetTimeStep[ 0 ];
            InitSolution[A];
            SaveSolution[A]; // Saves the solution x (from Ax = B) to .res file
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            InitSolution[B]; SaveSolution[B];
            For k In {1:N}
                InitSolution[CELL~{k}]; SaveSolution[CELL~{k}];
            EndFor
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.stranded_strands and dm.magnet.solve.formulation_parameters.rohf%}
            For k In {1:N_rohf}
                InitSolution[CELL_ROHF~{k}]; SaveSolution[CELL_ROHF~{k}];
            EndFor
            {% endif %}
            Evaluate[ $syscount = 0 ];
            Evaluate[ $saved = 1 ];
            Evaluate[ $elapsedCTI = 1 ]; // Number of control time instants already treated
            Evaluate[ $isCTI = 0 ];

            Evaluate[ $indicTotalLoss_dyn = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $indicCouplingLoss_dyn = 0 ]; // Put it to zero to avoid warnings

            // ----- Enter implicit Euler time integration loop (hand-made) -----
            // Avoid too close steps at the end. Stop the simulation if the step becomes ridiculously small
            SetExtrapolationOrder[ extrapolationOrder ];
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            Print[{$Time}, Format "%g 0.0 0.0 0.0 0.0 0.0", File outputPowerROHM];
            {% endif %}
            While[$Time < timeFinal - 1e-10] {
                SetTime[ $Time + $DTime ]; // Time instant at which we are looking for the solution
                SetTimeStep[ $TimeStep + 1 ];
                {% if dm.magnet.solve.formulation_parameters.rohm %}
                Generate[B];
                For k In {1:N}
                    Generate[CELL~{k}];
                EndFor
                {% endif %}
                {% if dm.magnet.solve.formulation_parameters.stranded_strands and dm.magnet.solve.formulation_parameters.rohf%}
                For k In {1:N_rohf}
                    Generate[CELL_ROHF~{k}];
                EndFor
                {% endif %}

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
                        {% if dm.magnet.solve.formulation_parameters.rohm %}
                        Generate[B]; Solve[B]; SaveSolution[B];
                        For k In {1:N}
                            Generate[CELL~{k}]; Solve[CELL~{k}]; SaveSolution[CELL~{k}];
                        EndFor
                        {% endif %}
                        {% if dm.magnet.solve.formulation_parameters.stranded_strands and dm.magnet.solve.formulation_parameters.rohf%}
                        For k In {1:N_rohf}
                            Generate[CELL_ROHF~{k}]; Solve[CELL_ROHF~{k}]; SaveSolution[CELL_ROHF~{k}];
                        EndFor
                        {% endif %}
                        {% if dm.magnet.solve.formulation_parameters.rohm %}
                        PostOperation[MagDyn_energy_full];
                        Print[{$Time, $saved}, Format "Saved time %g s (saved solution number %g). Output power infos:"];
                        Print[{$Time, $indicTotalLoss, $indicHystLoss, $indicHystCLoss, $indicCouplingLoss, $indicEddyLoss}, // the other loss contributions (interstrand and ROHF) are not integrated quantities, but computed from global quantities
                            Format "%g %14.12e %14.12e %14.12e %14.12e %14.12e %14.12e %14.12e", File outputPowerROHM];
                        {% endif %}
                        // Evaluate[$saved = $saved + 1];
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
                    {% if dm.magnet.solve.formulation_parameters.rohm %}
                    RemoveLastSolution[B];
                    {% endif %}
                    SetTime[$Time - $DTime];
                    SetTimeStep[$TimeStep - 1];
                    SetDTime[$dt_new];
                    // If it gets ridicoulously small, end the simulation, and report the information in crash file.
                    Test[ $dt_new < dt_max_var[]/10000 ]{
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
    // Frequency domain resolution
    { Name MagDyn_freq;
        System {
            {Name A; NameOfFormulation MagDyn_hphi_freq; Type ComplexValue;}
        }
        Operation {
            // Initialize directories
            CreateDirectory[resDirectory];
            DeleteFile[outputPowerROHM];
            DeleteFile[outputPowerROHF];
            DeleteFile[infoResidualFile];
            SetTimeStep[ 1 ];
            {% if dm.magnet.solve.frequency_domain_solver.frequency_sweep.run_sweep %}
            For i In {0:nbFreq-1}
                SetFrequency[A, freq(i)];
                Evaluate[$f = freq(i)];
                Print[{$f, $TimeStep}, Format "Start new solution. f: %g Hz. Solution: %g."];
                Generate[A]; Solve[A]; SaveSolution[A];
                PostOperation[MagDyn_energy];
                Print[{$indicTotalLoss}, Format "    - computed loss: %g."];
                SetTimeStep[$TimeStep + 1];
            EndFor
            {% else %}
            SetFrequency[A, f];
            Evaluate[$f = f];
            Print[{$f, $TimeStep}, Format "Start new solution. f: %g Hz. Solution: %g."];
            Generate[A]; Solve[A]; SaveSolution[A];
            PostOperation[MagDyn_energy];
            Print[{$indicTotalLoss}, Format "    - computed loss: %g."];
            {% endif %}
        }
    }

    {% if dm.magnet.solve.initial_conditions.init_from_pos_file %}
    { Name Projection_h_to_h;
        System {
            {Name Projection_h_to_h; NameOfFormulation Projection_h_to_h; DestinationSystem A ;}
        }
        Operation {
            GmshRead[StrCat["../", "<<dm.magnet.solve.initial_conditions.pos_file_to_init_from>>", ".pos"]]; // This file has to be in format without mesh (no -v2, here with GmshParsed format)
            Generate[Projection_h_to_h]; Solve[Projection_h_to_h];
            TransferSolution[Projection_h_to_h];
        }
    }
    {% endif %}
}

PostProcessing {
    {
    {% if dm.magnet.solve.frequency_domain_solver.enable %}
    Name MagDyn_hphi; NameOfFormulation MagDyn_hphi_freq;
    {% else %}
    Name MagDyn_hphi; NameOfFormulation MagDyn_hphi;
    {% endif %}
        Quantity {
            { Name phi; Value{ Local{ [ {dInv h} ] ;
                In OmegaCC_AndBnd; Jacobian Vol; } } }
            { Name h; Value{ Local{ [ {h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name b; Value {
                Term { [ mu[] * {h} ] ; In MagnLinDomain; Jacobian Vol; }
                {% if dm.magnet.solve.formulation_parameters.rohm %}
                Term { [ {b} ] ; In MagnHystDomain; Jacobian Vol; }
                {% endif %}
                }
            }
            { Name b_reaction; Value{
                Term { [ mu[] * ({h} - hsVal[]) ] ; In MagnLinDomain; Jacobian Vol; }
                {% if dm.magnet.solve.formulation_parameters.rohm %}
                Term { [ {b} - mu0*hsVal[]] ; In MagnHystDomain; Jacobian Vol; } // this is NOT the magnetization, just the reaction field
                {% endif %}
                }
            }
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            { Name m; Value{ Local{ [ {b} - mu0*{h} ] ;
                In MagnHystDomain; Jacobian Vol; } } }
            {% endif %} 
            { Name j; Value{ Local{ [ {d h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name jz; Value{ Local{ [ {d h} * Vector[0,0,1]] ;
                In Omega; Jacobian Vol; } } }
            { Name power_interstrand_coupling;
                Value {
                    Term{ [ 1/ell * {Iz} * {Iz} * R[] ] ; In Resistors; } 
                }
            }
            { Name strand_current;
                Value{
                    Integral{ [ {d h}*Vector[0,0,1] ] ;
                        In Strands ; Integration Int ; Jacobian Vol; }
                }
            }
            { Name coating_current;
                Value{
                    Integral{ [ {d h}*Vector[0,0,1] ] ;
                        In Coating ; Integration Int ; Jacobian Vol; }
                }
            }
            {% if dm.magnet.solve.frequency_domain_solver.enable %}
            { Name mean_strand_loss;
                Value{
                    Integral{ [ Re[ (rho[] * {d h} * Conj[{d h}] ) / 2 ] ] ;
                        In Strands ; Integration Int ; Jacobian Vol; } // only for massive strands (not stranded)
                }
            }
            { Name mean_coupling_loss;
                Value { 
                    Term{ [ ( 1/ell * Re[ {Iz} * Conj[{Iz}] ] * R[] ) / 2 ] ; In Resistors; } 
                }
            }
            { Name coupling_loss_per_cycle;
                Value { 
                    Term{ [ ( 1/ell * Re[ {Iz} * Conj[{Iz}] ] * R[] ) / (2*$f) ] ; In Resistors; } 
                }
            }
            { Name Iz_magnitude; Value { Term{ [ Sqrt[ {Iz} * Conj[{Iz}] ] ] ; In Resistors; } } }
            {% endif %}
            { Name totalLoss; // Obsolete!
                Value{
                    // Separate OmegaC into Matrix and nonlinear (resistivities take different argument types)
                    Integral{ [rho[{d h}, mu0*Norm[{h}]] * {d h} * {d h}] ; // j*e = rho*j^2 (filaments)
                        In NonLinOmegaC ; Integration Int ; Jacobian Vol; }
                    Integral{ [rho[mu0*Norm[{h}]] * {d h} * {d h}] ; // j*e = rho*j^2 (eddy)
                        In LinOmegaC ; Integration Int ; Jacobian Vol; }
                    {% if dm.magnet.solve.formulation_parameters.rohm %}
                    For k In {1:N}
                        Integral { [ 0.5 * ({h} - {g~{k}} + {h}[1] - {g~{k}}[1]) * w~{k} * mu0 * Dt[{hrev~{k}}] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                        Integral { [ w~{k} * tau_e~{k} * mu0 * SquNorm[Dt[{hrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                    For k In {2:N} // starts at k=2 to avoid division by 0 in the first cell, coupling time constant MUST indeed be zero for the first cell for this to make sense
                        Integral { [ hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}] * w~{k} * (mu0 * Dt[{hrev~{k}}] - mu0 * hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}]/tau_c~{k}) ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                        Integral { [ mu0 * SquNorm[hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}]]/tau_c~{k} * w~{k} ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                    {% endif %}
                    {% if dm.magnet.solve.formulation_parameters.rohf %}
                    // Pirr ROHF
                    For k In {1:N_rohf}
                        Term{ [ 0.5 * ({Is} - {G~{k}} + {Is}[1] - {G~{k}}[1]) * w_rohf~{k} * Lint0 * Dt[{Irev~{k}}] ] ; In Strands; } 
                        // Term{ [ 0.5 * ({Is} - {Irev~{k}} - tau_e_rohf~{k} * Dt[{Irev~{k}}] + {Is}[1] - {Irev~{k}}[1] - tau_e_rohf~{k} * Dt[{Irev~{k}}[1]]) * w_rohf~{k} * Lint0 * Dt[{Irev~{k}}] ] ; In Strands; } 
                    EndFor
                    // Peddy ROHF
                    For k In {1:N_rohf}
                        Term{ [ w_rohf~{k} * tau_e_rohf~{k} * Lint0 * SquNorm[Dt[{Irev~{k}}]] ] ; In Strands; } 
                    EndFor
                    Term{ [ {Is} * V_resistance[{Is}] ] ; In Strands; }
                    {% endif %}
                }
            }
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            { Name power_hyst;
                Value{
                    For k In {1:N}
                        Integral { [ 0.5 * ({h} - {g~{k}} + {h}[1] - {g~{k}}[1]) * w~{k} * mu0 * Dt[{hrev~{k}}] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                        // Integral { [ ({h} - {g~{k}}[1]) * w~{k} * mu0 * ({hrev~{k}} - {hrev~{k}}[1])/$DTime ] ;
                    EndFor
                }
            }
            { Name power_hyst_c;
                Value{
                    For k In {2:N} // starts at k=2 to avoid division by 0 in the first cell, coupling time constant MUST indeed be zero for the first cell for this to make sense
                        Integral { [ hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}] * w~{k} * (mu0 * Dt[{hrev~{k}}] - mu0 * hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}]/tau_c~{k}) ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_hyst_hyst_c_local;
                Value{
                    For k In {1:N}
                        Term { [ 0.5 * ({h} - {g~{k}} + {h}[1] - {g~{k}}[1]) * w~{k} * mu0 * Dt[{hrev~{k}}] ] ;
                            In MagnHystDomain; Jacobian Vol; }
                    EndFor
                    For k In {2:N}
                        Term { [ hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}] * w~{k} * (mu0 * Dt[{hrev~{k}}] - mu0 * hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}]/tau_c~{k}) ] ;
                            In MagnHystDomain ; Jacobian Vol; } 
                    EndFor
                }
            }
            { Name power_eddy;
                Value{
                    For k In {1:N}
                        Integral { [ w~{k} * tau_e~{k} * mu0 * SquNorm[Dt[{hrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_coupling;
                Value{
                    For k In {2:N} // starts at k=2 to avoid division by 0 in the first cell, coupling time constant MUST indeed be zero for the first cell for this to make sense
                        Integral { [ mu0 * SquNorm[hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c~{k}, chi~{k}]]/tau_c~{k} * w~{k} ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            {% endif %}
            // { Name surfaceArea; Value{ Local{ [ SurfaceArea[] ] ;
            //     In Coating; Jacobian Vol; } } }
            { Name I; Value { Term{ [ {I} ] ; In CoatingCut; } } }
            { Name V; Value { Term{ [ {V} ] ; In CoatingCut; } } }
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            { Name Ip; Value { Term{ [ {Ip} ] ; In PoweringCircuit; } } }
            { Name Vp; Value { Term{ [ {Vp} ] ; In PoweringCircuit; } } }
            {% endif %}
            { Name V_unitlen; Value { Term{ [ 1/ell * {V} ] ; In CoatingCut; } } }
            { Name Iz; Value { Term{ [ {Iz} ] ; In Resistors; } } }
            { Name Vz; Value { Term{ [ {Vz} ] ; In Resistors; } } }
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            { Name Is; Value { Term{ [ {Is} ] ; In Strands; } } }
            { Name Vs; Value { Term{ [ {Vs} ] ; In Strands; } } }  
            { Name Vs_unitlen; Value { Term{ [ 1/ell * {Vs} ] ; In Strands; } } }    
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.rohf %}
            // All ROHF quantities are defined on unit length
            { Name delta_fluxhyst; Value { Term{ [ DeltaFluxhyst_prev[{Is}, {Irev_1}, {Irev_2}, {Irev_3}, {Irev_4}, {Irev_5}] ] ; In Strands; } } }
            { Name delta_flux_local; Value { Term{ [ DeltaFluxhyst_prev[{Is}, {Irev_1}, {Irev_2}, {Irev_3}, {Irev_4}, {Irev_5}] ] ; In Strands; Jacobian Vol; } } }
            { Name delta_voltage_rohf; Value { Term{ [ Dt[ DeltaFluxhyst_prev[{Is}, {Irev_1}, {Irev_2}, {Irev_3}, {Irev_4}, {Irev_5}] ] ] ; In Strands; } } }
            { Name power_hyst_rohf;
                Value{
                    For k In {1:N_rohf}
                        Term{ [ 0.5 *({Is} - {G~{k}} + {Is}[1] - {G~{k}}[1]) * w_rohf~{k} * Lint0 * Dt[{Irev~{k}}] ]; In Strands; } 
                    EndFor
                }
            }
            { Name power_hyst_rohf_local;
                Value{
                    For k In {1:N_rohf}
                        Term{ [ 0.5 * ({Is} - {G~{k}} + {Is}[1] - {G~{k}}[1]) * w_rohf~{k} * Lint0 * Dt[{Irev~{k}}] / SurfaceArea[] ]; In Strands; Jacobian Vol;} 
                    EndFor
                }
            }
            { Name power_eddy_rohf;
                Value{
                    For k In {1:N_rohf}
                        Term{ [ w_rohf~{k} * tau_e_rohf~{k} * Lint0 * SquNorm[Dt[{Irev~{k}}]] ]; In Strands; } 
                    EndFor
                }
            }
            { Name power_joule;
                Value{
                    Term{ [ {Is} * V_resistance[{Is}] ] ; In Strands; }
                }
            }
            {% endif %}
            // Applied field (useful for magnetization plots)
            { Name hsVal; Value{ Term { [ hsVal[] ]; In Omega; } } }
            // Magnetization: integral of 1/2 * (r /\ j) in a conducting (sub-)domain
            { Name magnetization; Value{ Integral{ [ 0.5 * XYZ[] /\ {d h} ] ;
                In OmegaC_and_stranded; Integration Int; Jacobian Vol; } } }
            // Magnetic energy
            { Name magnetic_energy; Value{ Integral{ [ 0.5 * mu[] * {h} * {h} ] ;
                In Omega; Integration Int; Jacobian Vol; } } }
        }
    }
}
PostOperation {
    { Name MagDyn;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            // Local field solutions
            {% if dm.magnet.postproc.generate_pos_files%}
            Print[ b, OnElementsOf Omega , File StrCat["b.pos"], Name "b [T]" ];
            // Print[ surfaceArea, OnElementsOf Coating , File StrCat["surface.pos"], Name "surface [T]" ];
            // Print[ h, OnElementsOf Omega , File StrCat["h.pos"], Name "h [A/m]" ];
            // Print[ b_reaction, OnElementsOf Omega , File StrCat["br.pos"], Name "br [T]" ];
            Print[ j, OnElementsOf OmegaC_and_stranded , File StrCat["j.pos"], Name "j [A/m2]" ];
            Print[ jz, OnElementsOf OmegaC_and_stranded , File StrCat["jz.pos"], Name "jz [A/m2]" ];
            // Print[ j, OnElementsOf Coils , File StrCat["js.pos"], Name "js [A/m2]" ];
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            Print[ m, OnElementsOf MagnHystDomain , File StrCat["m.pos"], Name "m [T]" ];
            {% endif %}
            {% endif %}
            // Print[ b, OnPoint{3.86e-4,3.86e-4,0}, Format TimeTable, File StrCat[resDirectory, "/b_strand_1.txt"]];
            // Print[ h, OnPoint{3.86e-4,3.86e-4,0}, Format TimeTable, File StrCat[resDirectory, "/h_strand_1.txt"]];
            // Print[ b, OnPoint{2.309e-3,3.86e-4,0}, Format TimeTable, File StrCat[resDirectory, "/b_strand_3.txt"]];
            // Print[ h, OnPoint{2.309e-3,3.86e-4,0}, Format TimeTable, File StrCat[resDirectory, "/h_strand_3.txt"]];
            // Global solutions
            Print[ magnetization[OmegaC_and_stranded], OnGlobal, Format TimeTable, File StrCat[resDirectory, "/magn_total.txt"]];
            Print[ Iz, OnRegion Resistors, File StrCat[resDirectory,"/Iz.txt"], Format SimpleTable];
            // Print[strand_current[Strand_1], OnRegion Strand_1, File StrCat[resDirectory,"/Strand_current.txt"], Format SimpleTable];
            Print[coating_current[Coating], OnRegion Coating, File StrCat[resDirectory,"/Coating_current.txt"], Format SimpleTable];
            For i In {2:N_strands}
                Print[strand_current[Strand~{i}], OnRegion Strand~{i}, File > StrCat[resDirectory,"/Strand_current.txt"], Format SimpleTable];
            EndFor
            Print[Iz, OnRegion R_crossing_1, File StrCat[resDirectory,"/Coupling_current.txt"], Format SimpleTable];
            For i In {2:N_crossing_resistors}
                Print[Iz, OnRegion R_crossing~{i}, File > StrCat[resDirectory,"/Coupling_current.txt"], Format SimpleTable];
            EndFor
            // Print[Iz, OnRegion R_crossing_oblique_1, File StrCat[resDirectory,"/Coupling_oblique_current.txt"], Format SimpleTable];
            // For i In {2:N_strands}
            //     Print[Iz, OnRegion R_crossing_oblique~{i}, File > StrCat[resDirectory,"/Coupling_oblique_current.txt"], Format SimpleTable];
            // EndFor
            Print[Iz, OnRegion R_adjacent_1, File StrCat[resDirectory,"/Adjacent_current.txt"], Format SimpleTable];
            For i In {2:N_strands}
                Print[Iz, OnRegion R_adjacent~{i}, File > StrCat[resDirectory,"/Adjacent_current.txt"], Format SimpleTable];
            EndFor
            {% if dm.magnet.solve.frequency_domain_solver.enable %}
            // Frequency-domain solutions
            Print[ Iz_magnitude, OnRegion Resistors, File StrCat[resDirectory,"/Iz_magnitude.txt"], Format SimpleTable];
            Print[ mean_coupling_loss, OnRegion Resistors_crossing, File StrCat[resDirectory,"/Coupling_crossing_loss.txt"], Format SimpleTable];
            // Print[ mean_coupling_loss, OnRegion Resistors_crossing_oblique, File StrCat[resDirectory,"/Coupling_crossing_oblique_loss.txt"], Format SimpleTable];
            Print[ mean_coupling_loss, OnRegion Resistors_adjacent, File StrCat[resDirectory,"/Coupling_adjacent_loss.txt"], Format SimpleTable];
            Print[ mean_strand_loss[Strands], OnGlobal, File StrCat[resDirectory,"/Strand_loss.txt"], Format SimpleTable];
            {% else %}
            Print[ power_interstrand_coupling, OnRegion Resistors, File StrCat[resDirectory,"/power_IS_coupling.txt"], Format SimpleTable];
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.stranded_strands %}
            Print[ Is, OnRegion Strands, File StrCat[resDirectory,"/Is.txt"], Format SimpleTable];
            Print[ Vs, OnRegion Strands, File StrCat[resDirectory,"/Vs.txt"], Format SimpleTable];
            Print[ Vs_unitlen, OnRegion Strands, File StrCat[resDirectory,"/Vs_unitlen.txt"], Format SimpleTable];
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.rohf %}
            Print[ delta_fluxhyst, OnRegion Strands, File StrCat[resDirectory,"/delta_flux_hyst.txt"], Format SimpleTable];
            {% if dm.magnet.postproc.generate_pos_files%}
            Print[ delta_flux_local, OnElementsOf Strands , File StrCat["delta_flux_dens.pos"], Name "flux_dens [Wb/m3]" ];
            Print[ power_hyst_rohf_local, OnElementsOf Strands , File StrCat["p_hyst_ROHF.pos"], Name "p_hyst_ROHF [W/m3]" ];
            {% endif %}
            Print[ delta_voltage_rohf, OnRegion Strands, File StrCat[resDirectory,"/delta_voltage_ROHF.txt"], Format SimpleTable];
            Print[ power_hyst_rohf, OnRegion Strands, File StrCat[resDirectory,"/power_hyst_ROHF.txt"], Format SimpleTable];
            Print[ power_eddy_rohf, OnRegion Strands, File StrCat[resDirectory,"/power_eddy_ROHF.txt"], Format SimpleTable];
            Print[ power_joule, OnRegion Strands, File StrCat[resDirectory,"/power_joule.txt"], Format SimpleTable];
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.rohm%}
            {% if dm.magnet.postproc.generate_pos_files%}
            Print[ power_hyst_hyst_c_local, OnElementsOf MagnHystDomain , File StrCat["p_hyst_ROHM.pos"], Name "p_hyst_ROHM [W/m3]" ];
            {% endif %}
            {% endif %}
            Print[ I, OnRegion CoatingCut, File StrCat[resDirectory,"/It.txt"], Format SimpleTable];
            Print[ V, OnRegion CoatingCut, File StrCat[resDirectory,"/Vt.txt"], Format SimpleTable];
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            Print[ Ip, OnRegion PoweringCircuit, File StrCat[resDirectory,"/Ip.txt"], Format SimpleTable];
            Print[ Vp, OnRegion PoweringCircuit, File StrCat[resDirectory,"/Vp.txt"], Format SimpleTable];
            {% endif %}
            Print[ V_unitlen, OnRegion CoatingCut, File StrCat[resDirectory,"/Vt_unitlen.txt"], Format SimpleTable];
            {% if dm.magnet.postproc.save_last_magnetic_field != "None" %}
            // Last magnetic field solution for projection. Note the special format GmshParsed required for proper GmshRead[] operation in the later pre-resolution.
            Print[ h, OnElementsOf Omega, Format GmshParsed , File StrCat["../", "<<dm.magnet.postproc.save_last_magnetic_field>>", ".pos"], Name "h [A/m]", LastTimeStepOnly ];
            {% endif %}
        }
    }
    { Name MagDyn_energy; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ totalLoss[Omega], OnGlobal, Format Table, StoreInVariable $indicTotalLoss, File StrCat[resDirectory,"/dummy.txt"] ];
        }
    }
    { Name MagDyn_energy_full; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ totalLoss[Omega], OnGlobal, Format Table, StoreInVariable $indicTotalLoss, File StrCat[resDirectory,"/dummy.txt"] ];
            {% if dm.magnet.solve.formulation_parameters.rohm %}
            Print[ power_hyst[Omega], OnGlobal, Format Table, StoreInVariable $indicHystLoss, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_hyst_c[Omega], OnGlobal, Format Table, StoreInVariable $indicHystCLoss, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_coupling[Omega], OnGlobal, Format Table, StoreInVariable $indicCouplingLoss, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_eddy[Omega], OnGlobal, Format Table, StoreInVariable $indicEddyLoss, File StrCat[resDirectory,"/dummy.txt"] ];
            {% endif %}
            {% if dm.magnet.solve.formulation_parameters.rohf %}
            Print[ power_hyst_rohf, OnRegion Strands, Format Table, StoreInVariable $indicHystLossROHF, File StrCat[resDirectory,"/dummy.txt"] ]; // This only saved the power in a single strand into the Variable
            Print[ power_eddy_rohf, OnRegion Strands, Format Table, StoreInVariable $indicEddyLossROHF, File StrCat[resDirectory,"/dummy.txt"] ]; // This only saved the power in a single strand into the Variable
            Print[ power_joule, OnRegion Strands, Format Table, StoreInVariable $indicJouleLossROHF, File StrCat[resDirectory,"/dummy.txt"] ]; // This only saved the power in a single strand into the Variable
            {% endif %}
        }
    }
}