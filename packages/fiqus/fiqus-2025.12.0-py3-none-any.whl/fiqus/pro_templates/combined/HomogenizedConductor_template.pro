Group {
    // ------- PROBLEM DEFINITION -------
    // Cables
    Cables = Region[ {<<rm.powered.Cables.vol.numbers|join(', ')>>} ];
    BndCables = Region[ {<<rm.powered.Cables.surf.numbers|join(', ')>>} ];
    ArbitraryPointsCables = Region[ {<<rm.powered.Cables.curve.numbers|join(', ')>>} ];

    // Individual regions for the cables
    {% for i in range(0, len(rm.powered.Cables.vol.numbers)) %}
    Cable_<<i+1>> = Region[ {<<rm.powered.Cables.vol.numbers[i]>>} ];
    CableBnd_<<i+1>> = Region[ {<<rm.powered.Cables.surf.numbers[i]>>} ];
    {% endfor %}

    Air = Region[ {<<rm.air.vol.number>>} ];
    BndAir = Region[ {<<rm.air.surf.number>>} ];
    ArbitraryPointsAir = Region[ {<<rm.air.point.numbers|join(', ')>>} ]; 

    Coils = Region[ {<<rm.powered.ExcitationCoils.vol.numbers|join(', ')>>} ];
    BndCoils = Region[ {<<rm.powered.ExcitationCoils.surf.numbers|join(', ')>>} ];
    {% for i in range(0, len(rm.powered.ExcitationCoils.vol.numbers)) %}
    Coil_<<i+1>> = Region[ {<<rm.powered.ExcitationCoils.vol.numbers[i]>>} ];
    CoilBnd_<<i+1>> = Region[ {<<rm.powered.ExcitationCoils.surf.numbers[i]>>} ];
    {% endfor %}

    // Cuts
    CableCuts = Region[ {<<rm.powered.Cables.cochain.numbers|join(', ')>>} ];
    CoilCuts = Region[ {<<rm.powered.ExcitationCoils.cochain.numbers|join(', ')>>} ];
    Cuts = Region[ {CableCuts, CoilCuts} ]; // All the cuts 
    // Individual cuts for the cables
    {% for i in range(0, len(rm.powered.Cables.cochain.numbers)) %}
    CableCut_<<i+1>> = Region[ {<<rm.powered.Cables.cochain.numbers[i]>>} ];
    {% endfor %}
    // Individual cuts for the coils
    {% for i in range(0, len(rm.powered.ExcitationCoils.cochain.numbers)) %}
    CoilCut_<<i+1>> = Region[ {<<rm.powered.ExcitationCoils.cochain.numbers[i]>>} ];
    {% endfor %}
    
    // Gauge points - only air region
    ArbitraryPoints = Region[ {ArbitraryPointsAir} ];
    // Domain definitions
    OmegaCC = Region[ {Air, Coils} ];
    OmegaC = Region[ {Cables} ];
    Omega = Region[ {OmegaC, OmegaCC} ];
    BndOmegaC = Region[ {BndCables} ];
    BndOmega_ha = Region[ {BndOmegaC} ];
    // useful for function space definition
    Omega_AndBnd = Region[ {Omega, BndAir} ]; 
    OmegaC_AndBnd = Region[ {OmegaC, BndOmegaC} ];
    OmegaCC_AndBnd = Region[ {OmegaCC, BndOmegaC, BndAir} ];

    // Hysteresis regions
    {% if dm.magnet.solve.rohm.enable or dm.magnet.solve.rohf.enable %}
    MagnLinDomain = Region[ {Air, Coils} ];
    MagnHystDomain = Region[ {Cables} ];
    {% else %}
    MagnLinDomain = Region[ {Air, Coils, Cables} ];
    MagnHystDomain = Region[ {} ];
    {% endif %}

    // Formulation definitions
    {% if dm.magnet.solve.formulation_parameters.hphia %}
    Omega_h_OmegaCC_AndBnd = Region[ {BndOmegaC} ];
    Omega_h_AndBnd = Region[ {OmegaC, BndOmegaC} ];
    Omega_a_AndBnd = Region[ {OmegaCC, BndOmegaC, BndAir} ];
    Omega_a = Region[ {OmegaCC} ];
    {% else %}
    Omega_h_OmegaCC_AndBnd = Region[ {OmegaCC, BndOmegaC, BndAir} ];
    Omega_h_AndBnd = Region[ {Omega, BndAir} ];
    Omega_a_AndBnd = Region[ {} ];
    Omega_a = Region[ {} ];
    {% endif %}

    Gamma_h = Region[ {BndAir} ];
    Gamma_e = Region[ {} ];
    GammaAll = Region[ {Gamma_h, Gamma_e} ];

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
    N_cables = <<len(rm.powered.Cables.vol.numbers)>>;
    // Mixed formulation normal vector orientation
    normal_sign = 1; // could be -1 depending on how the geometry is built

    // ------------ DISCC MODEL PARAMETERS ------------
    // TO DO: generalize if several cables don't share the same properties
    // Independent inputs
    gamma_c = <<dm.magnet.solve.discc.gamma_c>>;
    gamma_a = <<dm.magnet.solve.discc.gamma_a>>;
    lambda_a = <<dm.magnet.solve.discc.lambda_a>>;
    Rc = <<dm.magnet.solve.discc.crossing_coupling_resistance>>;
    Ra = <<dm.magnet.solve.discc.adjacent_coupling_resistance>>;
    pitch_length = <<dm.magnet.solve.general_parameters.strand_transposition_length>>;
    n_strands = <<dm.magnet.solve.general_parameters.n_strands>>;
    strand_filling_factor = <<dm.magnet.solve.general_parameters.strand_filling_factor>>;
    cable_height = <<dm.magnet.geometry.cables_definition[0].height>>;
    cable_width = <<dm.magnet.geometry.cables_definition[0].width>>;
    // Equivalent conductivity tensor for the IS coupling current density field in DISCC
    strand_surf = strand_filling_factor * cable_width * cable_height / n_strands; // function of the cable size, number of strands and filling factor
    ref_periodicity_length = pitch_length/n_strands; // just for the definition of the contact resistivity based on the contact resistances
    rc = Rc * ref_periodicity_length * cable_width*2/n_strands * 0.5; // Ohm.m2, multiplication by 0.5 because the shape is a rhombus and not a rectangle
    ra = Ra * ref_periodicity_length * cable_height/2; // Ohm.m2
    common_mult = 2*pitch_length*pitch_length/(strand_filling_factor*cable_width*cable_width*cable_height); // (-)
    sigma_IS_xx = gamma_a * common_mult * (1/ra);
    sigma_IS_yy_crossing = gamma_c * common_mult * (1/rc);
    sigma_IS_yy_adjacent = lambda_a * common_mult * (1/ra);
    sigma_IS_yy = sigma_IS_yy_crossing + sigma_IS_yy_adjacent;
    sigma_IS[] = TensorDiag[sigma_IS_xx, sigma_IS_yy, 1];
    // Current grading factor
    ks_factor = 0.0;
    alpha_ks[] = 1 /(1 - ks_factor * 2 * X[] / cable_width); // TO DO: generalize (like this, it requires specific cable position and orientation)
        
    // ------- MATERIAL PARAMETERS - MAGNETIC -------
    mu0 = Pi*4e-7; // [H/m]
    nu0 = 1.0/mu0; // [m/H]
    mu[Air] = mu0;
    nu[Air] = nu0;
    mu[Coils] = mu0;
    nu[Coils] = nu0;

    // ------- MATERIAL PARAMETERS - ELECTRIC -------
    // TO DO: 
    //      - include b-dependence 
    //      - include T-dependence
    // Current sharing inputs
    strand_ic = <<dm.magnet.solve.current_sharing.superconductor_Ic>>;
    n = <<dm.magnet.solve.current_sharing.superconductor_n_value>>; // [-] power law index, one key parameter for the power law
    ec = 1e-4;
    jc_scaled[] = strand_ic / strand_surf * strand_filling_factor; // strand_filling_factor
    rho_matrix_scaled[] = <<dm.magnet.solve.current_sharing.matrix_resistance>> * strand_surf/strand_filling_factor; // scaled resistivity
    // Current sharing functions
    e_joule[] = CS_e_joule[$1, rho_matrix_scaled[], jc_scaled[], n]{ec};
    dedj_joule[] = CS_de_joule_dj[$1, rho_matrix_scaled[], jc_scaled[], n]{ec};

    // Resistivity for linear case (if we don't model the power law with current sharing) - used for debugging only
    rho[Cables] = <<dm.magnet.solve.general_parameters.rho_cables>>;

    {% if dm.magnet.solve.rohm.enable %}
    // ------- ROHM ------
    // TO DO: 
    //      - include I-dependence
    //      - include T-dependence
    // ROHM Model for cables - cell parameters from csv
    N_rohm = <<len(mp.rohm['alpha'])>>;
    weight_sc = strand_filling_factor; // strand filling factor
    tau_sc = <<dm.magnet.solve.rohm.tau_scaling>>;
    {% for i in range(1, 1+len(mp.rohm['alpha'])) %}

    {% if i == 1 %}
    w_rohm_<<i>> = <<mp.rohm['alpha'][i]>> * weight_sc; // + (1 - weight_sc); // first cell already contains eddy, such must not be scaled up. Instead, we add a linear contribution directly to the b(h) function
    {% else %}
    w_rohm_<<i>> = <<mp.rohm['alpha'][i]>> * weight_sc;
    {% endif %}
    kappa_rohm_<<i>> = <<mp.rohm['kappa'][i]>>;
    tau_e_rohm_<<i>> = <<mp.rohm['tau_e'][i]>> * tau_sc;
    tau_c_rohm_<<i>> = <<mp.rohm['tau_c'][i]>> * tau_sc;
    chi_rohm_<<i>> = <<mp.rohm['chi'][i]>>;
    {% endfor %}

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
    f_kappa[] = InterpolationLinear[$1]{List[list_f_kappa]};
    f_chi[] = (1 - $1/14)/(1 + $1/5);
    // f_kappa[] = (1 - $1/13)/(1 + $1/3); // TO DO: refine this scaling and introduce dependence on transport current
    // f_chi[] = (1 - $1/13)/(1 + $1/6); // TO DO: idem

    /* --- Functions for one cell only
    Function for reversible field only, for one cell
     $1: new field
     $2: reversible field at previous time step
     $3: rev+eddy+coupling field at previous time step
     $4: w_k,         weight for the considered cell k
     $5: kappa_k,     uncoupled irreversibility parameter for the considered cell k
     $6: chi_k,       coupled (minus uncoupled) irreversibility parameter for the considered cell k
     $7: tau_c_k,     coupling current time constant for the considered cell k
     $8: tau_e_k,     eddy current time constant for the considered cell k
    */
    hrev_k[] = ROHM_hRev[$1, $2, $3, $4, $5, $6, $7, $8, $DTime];
    
    /* Function for rev+eddy+coupling field, for one cell
     $1: new field
     $2: reversible field at previous time step
     $3: rev+eddy+coupling field at previous time step
     $4: irreversibility parameter for the considered cell k
    */
    g_k[] = ROHM_g[$1, $2, $3, $4];
    // Derivative of the reversible field, for one cell
    // Same parameters as the function for the reversible field $1 -> $8
    dhrev_k[] = ROHM_dhRev_dH[$1, $2, $3, $4, $5, $6, $7, $8, $DTime];
    
    /* Coupling field from time derivative of flux density b_k
     $1: \dot b_k
     $2: norm of b
     $3: tau_c_k
     $4: chi_k
    */
    hcoupling[] = ROHM_hCoupling[$1, f_chi[$2], $3, $4];
    
    /* --- Main hysteresis law
     $1: new field
     $2*k: reversible field at previous time step for cell k
     $2*k+1: g = rev+eddy+coupling field at previous time step for cell k
     $2*N+2: norm of b, for field-dependent parameters
    */
    bhyst[] = ROHM_bHyst[$1, <<len(mp.rohm['alpha'])>>,
    {% for i in range(1, 1+len(mp.rohm['alpha'])) %} $<<i*2>>, $<<i*2+1>>, w_rohm_<<i>>, f_kappa[$<<2*len(mp.rohm['alpha'])+2>>]*kappa_rohm_<<i>>, f_chi[$<<2*len(mp.rohm['alpha'])+2>>]*chi_rohm_<<i>>, tau_c_rohm_<<i>>, tau_e_rohm_<<i>>, {% endfor %} $DTime, weight_sc];

    // Derivative w.r.t. new field
    dbhystdh[] = ROHM_dbHyst_dH[$1, <<len(mp.rohm['alpha'])>>,
    {% for i in range(1, 1+len(mp.rohm['alpha'])) %} $<<i*2>>, $<<i*2+1>>, w_rohm_<<i>>, f_kappa[$<<2*len(mp.rohm['alpha'])+2>>]*kappa_rohm_<<i>>, f_chi[$<<2*len(mp.rohm['alpha'])+2>>]*chi_rohm_<<i>>, tau_c_rohm_<<i>>, tau_e_rohm_<<i>>, {% endfor %} $DTime, weight_sc];
   
    {% else %}
    // Non-hysteretic material (no ROHM model)
    mu[Cables] = mu0;
    nu[Cables] = nu0;
    {% endif %}

    {% if dm.magnet.solve.rohf.enable %}
    // ------- ROHF ------
    // TO DO: 
    //      - include b-dependence
    //      - include T-dependence
    Lint0 = (mu0 / (4*Pi)) * strand_surf / strand_filling_factor;
    N_rohf = <<len(mp.rohf['alpha'])>>;
    {% for i in range(1, 1+len(mp.rohf['alpha'])) %}

    w_rohf_<<i>> = <<mp.rohf['alpha'][i]>>;
    kappa_rohf_<<i>> = <<mp.rohf['kappa'][i]>> * strand_filling_factor / strand_surf;
    tau_e_rohf_<<i>> = <<mp.rohf['tau_e'][i]>>;
    {% endfor %}

    /* --- Test for a hysteresis element: gives the reversible current density in the static case
     $1: new current density
     $2: previous reversible + eddy current density
     $3: irreversibility parameter
    */
    /* --- Reversible current density per element
     $1: new current density
     $2: previous reversible current density
     $2: previous reversible + eddy current density
     $3: irreversibility parameter
     $4: eddy time constant
    */
    jrev_k[] = ROHF_jrev[$1, $2, $3, $4, $5, $DTime];
    jreveddy_k[] = ROHF_jreveddy[$1, $2, $3];
    
    /* --- Main hysteresis law
     $1: new current density
     $(2*k): previous reversible current densities
     $(2*k+1: previous reversible + eddy current densities
    */
    fluxdens[] = ROHF_fluxDensity[Lint0, $1, $DTime, <<len(mp.rohf['alpha'])>>,
    {% for i in range(1, 1+len(mp.rohf['alpha'])) %} w_rohf_<<i>>, $<<2*i>>, $<<2*i+1>>, 
    kappa_rohf_<<i>>, tau_e_rohf_<<i>>{% if not loop.last %}, {% endif %}
    {% endfor %}
    ];
    
    dfluxdensdj[] = ROHF_dFluxDensity_dJ[Lint0, $1, $DTime, <<len(mp.rohf['alpha'])>>,
    {% for i in range(1, 1+len(mp.rohf['alpha'])) %} w_rohf_<<i>>, $<<2*i>>, $<<2*i+1>>, 
    kappa_rohf_<<i>>, tau_e_rohf_<<i>>{% if not loop.last %}, {% endif %}
    {% endfor %}
    ];

    // --- Flux density based on known jrevs
    // $1 to $N: reversible current densities
    fluxdens_jrev[] = ROHF_fluxDensity_jrev[Lint0, <<len(mp.rohf['alpha'])>>,
    {% for i in range(1, 1+len(mp.rohf['alpha'])) %} w_rohf_<<i>>, $<<i>> {% if not loop.last %}, {% endif %}
    {% endfor %}
    ];

    {% endif %}

    {% if dm.magnet.solve.source_parameters.parallel_resistor %}
    // Parallel resistor
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
        directionApplied[] = Vector[Cos[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], Sin[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], 0.];

        constant_b[] = ($Time < ramp_duration ) ? InterpolationLinear[$Time]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>}]}  : <<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>;
        constant_b_prev[] = ($Time-$DTime < ramp_duration ) ? InterpolationLinear[$Time-$DTime]{List[{0,0,ramp_duration,<<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>}]}  : <<dm.magnet.solve.source_parameters.sine.superimposed_DC.field_magnitude>>;

        hsVal[] = nu0 * constant_b[] * constant_field_direction[] + nu0 * <<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * $Time] * directionApplied[];// * 200 * (X[] - 0.00625);
        hsVal_prev[] = nu0 * constant_b_prev[] * constant_field_direction[] + nu0 * <<dm.magnet.solve.source_parameters.sine.field_amplitude>> * Sin[2*Pi*f * ($Time-$DTime)] * directionApplied[];// * 200 * (X[] - 0.00625);

    {% elif dm.magnet.solve.source_parameters.source_type == 'piecewise' %}
        time_multiplier = <<dm.magnet.solve.source_parameters.piecewise.time_multiplier>>;
        applied_field_multiplier = <<dm.magnet.solve.source_parameters.piecewise.applied_field_multiplier>>;
        transport_current_multiplier = <<dm.magnet.solve.source_parameters.piecewise.transport_current_multiplier>>;
        directionApplied[] = Vector[Cos[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], Sin[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], 0.];

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
    I_1[] = + 2016 * (($Time < 2.0) ? 0.0 : 1.0) * Sin[2*Pi*f*$Time];
    I_2[] = - 2016 * (($Time < 2.0) ? 0.0 : 1.0) * Sin[2*Pi*f*$Time];
    js[Coil_1] = + 2016/(5e-3 * 1.4e-3) * (($Time < 2.0) ? 0.0 : 1.0) * Sin[2*Pi*f*$Time] * Vector[0,0,1];
    js[Coil_2] = - 2016/(5e-3 * 1.4e-3) * (($Time < 2.0) ? 0.0 : 1.0) * Sin[2*Pi*f*$Time] * Vector[0,0,1];
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
    
    iter_max = 50; // Maximum number of iterations (after which we exit the iterative loop)
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
    outputPowerFull = StrCat[resDirectory,"/power_full.txt"]; // File updated during runtime
    outputPowerROHM = StrCat[resDirectory,"/power_ROHM.txt"]; // File updated during runtime
    outputPowerROHF = StrCat[resDirectory,"/power_ROHF.txt"]; // File updated during runtime
    pcrossingFile = StrCat[resDirectory,"/p_crossing.txt"];
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
    { Name a ;
        Case {
            {Region GammaAll ; Value -X[] * mu0 ; TimeFunction hsVal[] ;}
        }
    }
    { Name h ; Case {} }
    { Name Voltage ; Case {} }
    { Name k ; Case {} }

    { Name Current ;
        Case {
            {% if not dm.magnet.solve.source_parameters.parallel_resistor %}
            {% for i in range(len(rm.powered.Cables.cochain.numbers)) %}
            {% if dm.magnet.solve.source_parameters.cable_current_multipliers is none %}
            {Region CableCut_<<i+1>> ; Type Assign ; Value 1.0 ; TimeFunction I_transport[] ;}
            {% else %}
            {Region CableCut_<<i+1>> ; Type Assign ; Value <<dm.magnet.solve.source_parameters.cable_current_multipliers[i]>> ; TimeFunction I_transport[] ;} 
            {% endif %}
            {% endfor %}
            {% endif %}
            {% if dm.magnet.solve.initial_conditions.init_from_pos_file %}
            {Region Cuts ; Type InitFromResolution ; NameOfResolution Projection_h_to_h ;}
            {% endif %}
        }
    }

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
    {% if dm.magnet.solve.source_parameters.parallel_resistor %}
    { Name Current_Cir_transport ; 
        Case {
            {Region CurrentSource ; Value 1.0 ; TimeFunction I_transport[] ;}
        } 
    } // Empty to avoid warnings
    { Name Voltage_Cir_transport ; Case {} } // Empty to avoid warnings
    {Name ElectricalCircuit_transport ; Type Network ;
        Case circuit1 {
            // TO DO HERE
            {% for i in range(len(rm.powered.Cables.cochain.numbers)) %}
            {% if dm.magnet.solve.source_parameters.cable_current_multipliers[i] > 0.0 %}
            {Region CableCut_<<i+1>> ; Branch {<<i>>, <<i+1>>} ;}
            {% else %}
            {Region CableCut_<<i+1>> ; Branch {<<i+1>>, <<i>>} ;}
            {% endif %}
            {% endfor %}
            {Region CurrentSource ; Branch { <<len(rm.powered.Cables.cochain.numbers)>>, 0 } ;}
            {Region ParallelResistor ; Branch { <<len(rm.powered.Cables.cochain.numbers)>>, 0 } ;}
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
                    { GeoElement Quadrangle ; NumberOfPoints 4 ; }
                }
            }
        }
    }
    // For hysteretic element, integration of {b} and bhyst[{h}], which should be accounted for as constant per element
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

{% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
For i In {1 : <<len(rm.powered.ExcitationCoils.vol.numbers)>>}
    FunctionSpace {        
        // Function space for the source field (defined during pre-resolution, and then included as a sub-space in the main h_space)
        { Name hs_coil_space~{i}; Type Form1;
            BasisFunction {
                { Name psie; NameOfCoef he; Function BF_Edge;
                    Support Coil~{i}; Entity EdgesOf[All, Not CoilBnd~{i}]; }
                { Name sc; NameOfCoef Ii; Function BF_GroupOfEdges;
                    Support Omega; Entity GroupsOfEdgesOf[CoilCut~{i}]; }
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
                Galerkin { [  - Is0[]/SurfaceArea[], {d hs} ] ;
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
                Support Omega_h_OmegaCC_AndBnd; Entity NodesOf[OmegaCC]; } // Extend support to boundary for surface integration (e.g. useful for weak B.C.)
            { Name gradpsin; NameOfCoef phin2; Function BF_GroupOfEdges;
                Support OmegaC; Entity GroupsOfEdgesOnNodesOf[BndOmegaC]; } // To treat properly the Omega_CC-Omega_C boundary
            { Name psie; NameOfCoef he; Function BF_Edge;
                Support OmegaC_AndBnd; Entity EdgesOf[All, Not BndOmegaC]; }
            { Name sc; NameOfCoef Ii; Function BF_GroupOfEdges;
                Support Omega_h_AndBnd; Entity GroupsOfEdgesOf[CableCuts]; } // The region Cuts contains the union of all the relevant cuts (cohomology basis function support) 
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable and not dm.magnet.solve.formulation_parameters.hphia %}
            { Name sb_coil ; NameOfCoef Ic ;  // Global Basis Function
                Function BF_Global { 
                    Quantity hs ;
                    Formulation js_to_hs_coil {<<len(rm.powered.ExcitationCoils.vol.numbers)>>} ;
                    Group Coils ; Resolution js_to_hs_coil {<<len(rm.powered.ExcitationCoils.vol.numbers)>>} ;
                } ;
                Support Omega ; Entity Global [Coils] ; }
            {% endif %}
        }
        GlobalQuantity {
            { Name I ; Type AliasOf        ; NameOfCoef Ii ; }
            { Name V ; Type AssociatedWith ; NameOfCoef Ii ; }
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable and not dm.magnet.solve.formulation_parameters.hphia %}
            { Name Ic ; Type AliasOf        ; NameOfCoef Ic ; }
            { Name Vc ; Type AssociatedWith ; NameOfCoef Ic ; }
            {% endif %}
        }
        Constraint {
            { NameOfCoef he; EntityType EdgesOf; NameOfConstraint h; }
            { NameOfCoef phin; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef phin2; EntityType NodesOf; NameOfConstraint phi; }
            { NameOfCoef Ii ; EntityType GroupsOfEdgesOf ; NameOfConstraint Current ; }
            { NameOfCoef V ; EntityType GroupsOfNodesOf ; NameOfConstraint Voltage ; }
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable and not dm.magnet.solve.formulation_parameters.hphia %}
            { NameOfCoef Ic ; EntityType Region ; NameOfConstraint Current_coil ; }
            { NameOfCoef Vc ; EntityType Region ; NameOfConstraint Voltage_coil ; }
            {% endif %}
        }
    }
    // Function space for the interstrand coupling currents
    { Name k_space; Type Form1;
        BasisFunction {
            { Name kc; NameOfCoef ke; Function BF_Edge;
                Support Region[{OmegaC_AndBnd}]; Entity EdgesOf[All, Not BndOmegaC]; } // Extend support to boundary for surface integration (e.g. useful for weak B.C.)
        }   
        Constraint {
            { NameOfCoef ke; EntityType EdgesOf; NameOfConstraint k; }
        }
    }
    {% if dm.magnet.solve.rohm.enable %}
    // Function space for b from ROHM.
    { Name b_or_h_space ; Type Vector;
        BasisFunction {
            { Name sex ; NameOfCoef aex ; Function BF_VolumeX ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
            { Name sey ; NameOfCoef aey ; Function BF_VolumeY ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
        }
    }
    // Function space for internal state variable with ROHM (h_rev for each cell)
    For k In {1:N_rohm}
        { Name hrev~{k} ; Type Form1;
            BasisFunction {
                { Name psie; NameOfCoef he; Function BF_Edge;
                    Support MagnHystDomain; Entity EdgesOf[All]; }
                // { Name sex ; NameOfCoef aex ; Function BF_VolumeX ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
                // { Name sey ; NameOfCoef aey ; Function BF_VolumeY ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
            }
        }
        // We can also recompute it, instead of saving it. To be seen which approach is the best.
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
    {% if dm.magnet.solve.rohf.enable %}
    // Function space for j from ROHF. Element-wise constant functions
    { Name flux_space ; Type Vector;
        BasisFunction {
            { Name sez ; NameOfCoef aez ; Function BF_VolumeZ ; Support MagnHystDomain ; Entity VolumesOf[ All ] ; }
        }
    }
    // Function space for internal state variable with ROHF (j_rev for each cell)
    For k In {1:N_rohf}
        { Name jrev~{k} ; Type Vector;
            BasisFunction {
                { Name psiv; NameOfCoef jv; Function BF_VolumeZ;
                    Support MagnHystDomain; Entity VolumesOf[All]; }
            }
        }
        { Name jreveddy~{k} ; Type Vector;
            BasisFunction {
                { Name psive; NameOfCoef jve; Function BF_VolumeZ;
                    Support MagnHystDomain; Entity VolumesOf[All]; }
            }
        }
    EndFor
    {% endif %}
    // Function space for vector potential in the mixed formulation
    { Name a_space_2D; Type Form1P;
        BasisFunction {
            { Name psin; NameOfCoef an; Function BF_PerpendicularEdge;
                Support Omega_a_AndBnd; Entity NodesOf[All]; }
            { Name psin2; NameOfCoef an2; Function BF_PerpendicularEdge_2E;
                Support Omega_a_AndBnd; Entity EdgesOf[BndOmegaC]; }
        }
        Constraint {
            { NameOfCoef an; EntityType NodesOf; NameOfConstraint a; }
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
}

Formulation{
    // h-formulation
    { Name MagDyn_hphi; Type FemEquation;
        Quantity {
            // Functions for the out-of-plane (OOP) problem
            { Name h; Type Local; NameOfSpace h_space; }
            { Name hp; Type Local; NameOfSpace h_space; }
            { Name I; Type Global; NameOfSpace h_space[I]; }
            { Name V; Type Global; NameOfSpace h_space[V]; }
            {% if dm.magnet.solve.rohm.enable %}
            // ROHM model
            { Name b; Type Local; NameOfSpace b_or_h_space; }
            For k In {1:N_rohm}
                { Name hrev~{k}; Type Local; NameOfSpace hrev~{k};}
                { Name g~{k}; Type Local; NameOfSpace g~{k};}
            EndFor
            {% endif %}
            {% if dm.magnet.solve.rohf.enable %}
            // ROHF model
            { Name flux; Type Local; NameOfSpace flux_space; }
            For k In {1:N_rohf}
                { Name jrev~{k}; Type Local; NameOfSpace jrev~{k}; }
                { Name jreveddy~{k}; Type Local; NameOfSpace jreveddy~{k}; }
            EndFor
            {% endif %}
            // IS coupling currents
            { Name k_IS; Type Local; NameOfSpace k_space; }
            {% if dm.magnet.solve.formulation_parameters.hphia %}
            // h-phi-a
            { Name a; Type Local; NameOfSpace a_space_2D; }
            {% else %}
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            // excitation coils
            { Name Ic ; Type Global; NameOfSpace h_space[Ic]; }
            { Name Vc ; Type Global; NameOfSpace h_space[Vc]; }
            {% endif %}
            {% endif %}
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            { Name Ip ; Type Global; NameOfSpace ElectricalCircuit_transport[Ip]; }
            { Name Vp ; Type Global; NameOfSpace ElectricalCircuit_transport[Vp]; }
            {% endif %}
        }
        Equation {
            // --- Axial currents problem ---
            // Time derivative of b (NonMagnDomain)
            Galerkin { [ mu[] * Dof{h} / $DTime , {h} ];
                In MagnLinDomain; Integration Int; Jacobian Vol;  }
            Galerkin { [ -mu[] * {h}[1] / $DTime , {h} ];
                In MagnLinDomain; Integration Int; Jacobian Vol;  } 

            {% if dm.magnet.solve.rohf.enable %}
            // ROHF model for the current flowing in the strands
            {% if not dm.magnet.solve.rohm.enable %}
            // Time derivative of b (in MagnHystDomain if no ROHM)
            Galerkin { [ mu[] * Dof{h} / $DTime , {h} ];
                In MagnHystDomain; Integration Int; Jacobian Vol;  }
            Galerkin { [ -mu[] * {h}[1] / $DTime , {h} ];
                In MagnHystDomain; Integration Int; Jacobian Vol;  } 
            {% endif %}
            Galerkin { [ fluxdens[{d h}{% for i in range(1, 1+len(mp.rohf['alpha'])) %}, {jrev_<<i>>}[1], {jreveddy_<<i>>}[1]{% endfor %}] / $DTime , {d h} ];
                In MagnHystDomain; Integration Int; Jacobian Vol;  }
            Galerkin { [ dfluxdensdj[{d h}{% for i in range(1, 1+len(mp.rohf['alpha'])) %}, {jrev_<<i>>}[1], {jreveddy_<<i>>}[1]{% endfor %}] * Dof{d h} / $DTime , {d hp} ];
                In MagnHystDomain; Integration Int; Jacobian Vol;  }
            Galerkin { [ - dfluxdensdj[{d h}{% for i in range(1, 1+len(mp.rohf['alpha'])) %}, {jrev_<<i>>}[1], {jreveddy_<<i>>}[1]{% endfor %}] * {d h} / $DTime , {d hp} ];
                In MagnHystDomain; Integration Int; Jacobian Vol;  }
            Galerkin { [ - {flux}[1] / $DTime , {d h} ];
                In MagnHystDomain; Integration Int; Jacobian Vol;  }
            {% endif %}
            {% if dm.magnet.solve.rohm.enable %}
            // ROHM
            // Templated for N cells
            Galerkin { [ bhyst[{h},{% for i in range(1, 1+len(mp.rohm['alpha'])) %} {hrev_<<i>>}[1], {g_<<i>>}[1],{% endfor %} Norm[{b}]] / $DTime , {h} ];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ dbhystdh[{h},{% for i in range(1, 1+len(mp.rohm['alpha'])) %} {hrev_<<i>>}[1], {g_<<i>>}[1],{% endfor %} Norm[{b}]] * Dof{h} / $DTime , {hp}];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ - dbhystdh[{h},{% for i in range(1, 1+len(mp.rohm['alpha'])) %} {hrev_<<i>>}[1], {g_<<i>>}[1],{% endfor %} Norm[{b}]] * {h}  / $DTime , {hp}];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            Galerkin { [ - {b}[1] / $DTime , {h} ];
                In MagnHystDomain; Integration Int_b; Jacobian Vol;  }
            {% endif %}

            {% if dm.magnet.solve.general_parameters.superconductor_linear %}
            // Eddy current (linear OmegaC)
            Galerkin { [ rho[] * Dof{d h} , {d h} ];
                In OmegaC; Integration Int; Jacobian Vol;  }   
            {% else %}     
            Galerkin { [ e_joule[{d h}] , {d h} ]; // h based
                In OmegaC; Integration Int; Jacobian Vol;  }
            Galerkin { [ dedj_joule[{d h}] * Dof{d h} , {d hp} ];
                In OmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method
            Galerkin { [ - dedj_joule[{d h}] * {d h} , {d hp} ];
                In OmegaC; Integration Int; Jacobian Vol;  } // For Newton-Raphson method    
            {% endif %}

            // Induced currents (Global var)
            GlobalTerm { [ Dof{V} , {I} ] ; In CableCuts ; }

            // Insterstrand coupling current coupling term
            Galerkin { [ Dof{d k_IS} , {d h} ];
                In OmegaC; Integration Int; Jacobian Vol;  }
            // Interstrand coupling current formulation
            Galerkin { [ - sigma_IS[] * Dof{k_IS} , {k_IS} ];
                In OmegaC; Integration Int; Jacobian Vol;  }
            Galerkin { [ alpha_ks[] * Dof{d h} , {d k_IS} ];
                In OmegaC; Integration Int; Jacobian Vol;  }

            // a-formulation in the mixed formulation
            {% if dm.magnet.solve.formulation_parameters.hphia %}
            Galerkin { [ nu[] * Dof{d a} , {d a} ];
                In Omega_a; Integration Int; Jacobian Vol; }
            // Coupling terms
            Galerkin { [ + normal_sign * Dof{a} /\ Normal[] /$DTime , {h}];
                In BndOmega_ha; Integration Int; Jacobian Sur; }
            Galerkin { [ - normal_sign * {a}[1] /\ Normal[] /$DTime , {h}];
                In BndOmega_ha; Integration Int; Jacobian Sur; }
            Galerkin { [ normal_sign * Dof{h} /\ Normal[] , {a}];
                In BndOmega_ha; Integration Int; Jacobian Sur; }
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            Galerkin { [ -js[] , {a} ];
                In Coils; Integration Int; Jacobian Vol; }
            {% endif %}
            {% else %}
            // Natural boundary condition
            Galerkin { [ - dbsdt[] * Normal[] , {dInv h} ];
                In BndAir; Integration Int; Jacobian Sur;  }
            {% if dm.magnet.solve.source_parameters.excitation_coils.enable %}
            GlobalTerm { [ Dof{Vc} , {Ic} ] ; In CoilCuts ; }
            {% endif %}
            {% endif %}
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            GlobalTerm{ [ Dof{Vp} , {Ip} ]; In ParallelResistor; }
            GlobalTerm{ [ R[] * Dof{Ip} , {Ip} ]; In ParallelResistor; }
            // Circuit network for transport current and voltage
            GlobalEquation {
                Type Network ; NameOfConstraint ElectricalCircuit_transport ;
                { Node {I};  Loop {V};  Equation {V};  In CableCuts ; }
                { Node {Ip}; Loop {Vp}; Equation {Vp}; In PoweringCircuit; }
          	}
            {% endif %}
        }
    }
    // Frequency domain formulation
    { Name MagDyn_hphi_freq; Type FemEquation;
        Quantity {
            // Functions for the out-of-plane (OOP) problem
            { Name h; Type Local; NameOfSpace h_space; }
            { Name I; Type Global; NameOfSpace h_space[I]; }
            { Name V; Type Global; NameOfSpace h_space[V]; }
            { Name k_IS; Type Local; NameOfSpace k_space; }
        }
        Equation {
            // --- OOP problem ---
            // Time derivative of b (NonMagnDomain)
            Galerkin { DtDof[ mu[] * Dof{h}, {h} ];
                In Omega; Integration Int; Jacobian Vol;  }
            
            Galerkin { [ Dof{d k_IS} , {d h} ];
                In OmegaC; Integration Int; Jacobian Vol;  }

            // Natural boundary condition for normal flux density (useful when transport current is an essential condition)
            {% if dm.magnet.solve.source_parameters.boundary_condition_type == 'Natural' %}
            Galerkin { [ - Complex[0, 2*Pi*$f*bmax]*Vector[Cos[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], Sin[<<dm.magnet.solve.source_parameters.field_angle>>*Pi/180], 0.] * Normal[] , {dInv h} ]; 
                In BndAir; Integration Int; Jacobian Sur;  }
            {% endif %}

            Galerkin { [ - sigma_IS[] * Dof{k_IS} , {k_IS} ];
                In OmegaC; Integration Int; Jacobian Vol;  }
            Galerkin { [ alpha_ks[] * Dof{d h} , {d k_IS} ];
                In OmegaC; Integration Int; Jacobian Vol;  }

            // Global term
            GlobalTerm { [ Dof{V} , {I} ] ; In Cuts ; }
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
    {% if dm.magnet.solve.rohm.enable %}
    // Update of b in hysteresis model
    { Name Update_b; Type FemEquation ;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
            { Name b ; Type Local ; NameOfSpace b_or_h_space ; }
            For k In {1:N_rohm}
                { Name hrev~{k}  ; Type Local ; NameOfSpace hrev~{k};}
                { Name g~{k}  ; Type Local ; NameOfSpace g~{k};}
            EndFor
        }
        Equation {
            Galerkin { [ Dof{b} , {b} ];
                In MagnHystDomain; Jacobian Vol; Integration Int; }
            // Templated for N cells
            Galerkin { [ - bhyst[{h},{% for i in range(1, 1+len(mp.rohm['alpha'])) %} {hrev_<<i>>}[1], {g_<<i>>}[1],{% endfor %} Norm[{b}]] , {b} ]; 
                In MagnHystDomain; Jacobian Vol; Integration Int; }
        }
    }
    // Update of internal variables
    For k In {1:N_rohm}
        { Name Update_hrev~{k} ; Type FemEquation ;
            Quantity {
                { Name h; Type Local; NameOfSpace h_space; }
                { Name b; Type Local; NameOfSpace b_or_h_space; }
                { Name hrev~{k}  ; Type Local ; NameOfSpace hrev~{k};}
                { Name g~{k}  ; Type Local ; NameOfSpace g~{k};}
            }
            Equation {
                Galerkin { [ Dof{hrev~{k}}, {hrev~{k}} ];
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ - hrev_k[{h}, {hrev~{k}}[1], {g~{k}}[1], w_rohm~{k}, f_kappa[Norm[{b}]]*kappa_rohm~{k}, f_chi[Norm[{b}]]*chi_rohm~{k}, tau_c_rohm~{k}, tau_e_rohm~{k}], {hrev~{k}} ] ;
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ Dof{g~{k}}, {g~{k}} ];
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ - g_k[{h}, {hrev~{k}}[1], {g~{k}}[1], f_kappa[Norm[{b}]]*kappa_rohm~{k}], {g~{k}} ] ;
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
            }
        }
    EndFor
    {% endif %}
    {% if dm.magnet.solve.rohf.enable %}
    // Update of flux in hysteresis model
    { Name Update_flux; Type FemEquation ;
        Quantity {
            { Name h; Type Local; NameOfSpace h_space; }
            { Name flux; Type Local; NameOfSpace flux_space; }
            For k In {1:N_rohf}
                { Name jrev~{k}  ; Type Local ; NameOfSpace jrev~{k};}
                { Name jreveddy~{k}  ; Type Local ; NameOfSpace jreveddy~{k};}
            EndFor
        }
        Equation {
            Galerkin { [ Dof{flux} , {flux} ];
                In MagnHystDomain; Jacobian Vol; Integration Int; }
            // Templated for N cells 
            Galerkin { [ - fluxdens[{d h} {% for i in range(1, 1+len(mp.rohf['alpha'])) %}, {jrev_<<i>>}[1], {jreveddy_<<i>>}[1]{% endfor %}], {flux} ];
                In MagnHystDomain; Jacobian Vol; Integration Int; }
        }
    }
    // Update of internal variables
    For k In {1:N_rohf}
        { Name Update_jrev~{k} ; Type FemEquation ;
            Quantity {
                { Name h; Type Local; NameOfSpace h_space; }
                { Name jrev~{k}  ; Type Local ; NameOfSpace jrev~{k};}
                { Name jreveddy~{k}; Type Local; NameOfSpace jreveddy~{k}; }
            }
            Equation {
                Galerkin { [ Dof{jrev~{k}}, {jrev~{k}} ];
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ - jrev_k[{d h}, {jrev~{k}}[1], {jreveddy~{k}}[1], kappa_rohf~{k}, tau_e_rohf~{k}], {jrev~{k}} ] ;
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ Dof{jreveddy~{k}}, {jreveddy~{k}} ];
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
                Galerkin { [ - jreveddy_k[{d h}, {jreveddy~{k}}[1], kappa_rohf~{k}], {jreveddy~{k}} ] ;
                    In MagnHystDomain; Jacobian Vol; Integration Int; }
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
    Print[{$iter, $res, $res / $res0, $indicLoss},
        Format "%g %14.12e %14.12e %14.12e", File infoResidualFile];
    // ----- Enter the iterative loop (hand-made) -----
    While[$convCrit > 1 && $res / $res0 <= 1e10 && $iter < iter_max]{
        Solve[A]; Evaluate[ $syscount = $syscount + 1 ];
        {% if dm.magnet.solve.rohm.enable %}
        Generate[B_OR_H]; Solve[B_OR_H]; // update {b} so that the field-dependent parameter is updated for the convergence criterion
        {% endif %}
        {% if dm.magnet.solve.rohf.enable %}
        Generate[FLUX]; Solve[FLUX]; // update {flux} so that the field-dependent parameter is updated for the convergence criterion
        {% endif %}
        Generate[A]; GetResidual[A, $res];
        Evaluate[ $iter = $iter + 1 ];
        Evaluate[ $indicLossOld = $indicLoss];
        PostOperation[MagDyn_energy];
        Print[{$iter, $res, $res / $res0, $indicLoss},
            Format "%g %14.12e %14.12e %14.12e", File infoResidualFile]; // Here, the loss is not the real one, as the memory fields used to compute it are not updated yet (for efficiency). To be possibly modified if this gets annoying.
        // Evaluate the convergence indicator
        Evaluate[ $relChangeACLoss = Abs[($indicLossOld - $indicLoss)/((Abs[$indicLossOld]>1e-7 || $iter < 10) ? $indicLossOld:1e-7)] ];
        Evaluate[ $convCrit = $relChangeACLoss/tol_energy];
    }
Return

Resolution {
    { Name MagDyn;
        System {
            {Name A; NameOfFormulation MagDyn_hphi;}
            {% if dm.magnet.solve.rohm.enable %}
            {Name B_OR_H; NameOfFormulation Update_b; }
            For k In {1:N_rohm}
                {Name CELL_ROHM~{k}; NameOfFormulation Update_hrev~{k}; }
            EndFor
            {% endif %}
            {% if dm.magnet.solve.rohf.enable %}
            {Name FLUX; NameOfFormulation Update_flux; }
            For k In {1:N_rohf}
                {Name CELL_ROHF~{k}; NameOfFormulation Update_jrev~{k}; }
            EndFor
            {% endif %}
        }
        Operation {
            // Initialize directories
            CreateDirectory[resDirectory];
            DeleteFile[outputPowerFull];
            DeleteFile[outputPowerROHM];
            DeleteFile[outputPowerROHF];
            DeleteFile[infoResidualFile];
            // Initialize the solution (initial condition)
            SetTime[ timeStart ];
            SetDTime[ dt ];
            SetTimeStep[ 0 ];
            InitSolution[A];
            SaveSolution[A]; // Saves the solution x (from Ax = B) to .res file
            {% if dm.magnet.solve.rohm.enable %}
            InitSolution[B_OR_H]; SaveSolution[B_OR_H];
            For k In {1:N_rohm}
                InitSolution[CELL_ROHM~{k}]; SaveSolution[CELL_ROHM~{k}];
            EndFor
            {% endif %}
            {% if dm.magnet.solve.rohf.enable %}
            InitSolution[FLUX]; SaveSolution[FLUX];
            For k In {1:N_rohf}
                InitSolution[CELL_ROHF~{k}]; SaveSolution[CELL_ROHF~{k}];
            EndFor
            {% endif %}
            Evaluate[ $syscount = 0 ];
            Evaluate[ $saved = 1 ];
            Evaluate[ $elapsedCTI = 1 ]; // Number of control time instants already treated
            Evaluate[ $isCTI = 0 ];

            Evaluate[ $indicLoss = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_tot = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_hyst_ROHM = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_hyst_c_ROHM = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_coupling_ROHM = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_eddy_ROHM = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_IS_coupling = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_hyst_ROHF = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_eddy_ROHF = 0 ]; // Put it to zero to avoid warnings
            Evaluate[ $power_ohmic = 0 ]; // Put it to zero to avoid warnings
            // ----- Enter implicit Euler time integration loop (hand-made) -----
            // Avoid too close steps at the end. Stop the simulation if the step becomes ridiculously small
            SetExtrapolationOrder[ extrapolationOrder ];
            // Print[{$Time}, Format "%g 0.0 0.0 0.0 0.0 0.0", File outputPower];
            While[$Time < timeFinal] {
                SetTime[ $Time + $DTime ]; // Time instant at which we are looking for the solution
                SetTimeStep[ $TimeStep + 1 ];
                {% if dm.magnet.solve.rohm.enable %}
                Generate[B_OR_H];
                For k In {1:N_rohm}
                    Generate[CELL_ROHM~{k}];
                EndFor
                {% endif %}
                {% if dm.magnet.solve.rohf.enable %}
                Generate[FLUX];
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
                        {% if dm.magnet.solve.rohm.enable %}
                        Generate[B_OR_H]; Solve[B_OR_H]; SaveSolution[B_OR_H];
                        For k In {1:N_rohm}
                            Generate[CELL_ROHM~{k}]; Solve[CELL_ROHM~{k}]; SaveSolution[CELL_ROHM~{k}];
                        EndFor
                        {% endif %}
                        {% if dm.magnet.solve.rohf.enable %}
                        Generate[FLUX]; Solve[FLUX]; SaveSolution[FLUX];
                        For k In {1:N_rohf}
                            Generate[CELL_ROHF~{k}]; Solve[CELL_ROHF~{k}]; SaveSolution[CELL_ROHF~{k}];
                        EndFor
                        {% endif %}

                        PostOperation[MagDyn_energy_full];
                        Print[{$Time, $saved}, Format "Saved time %g s (saved solution number %g). Output power infos:"];
                        Print[{$Time, $power_tot, $power_hyst_ROHM, $power_hyst_c_ROHM, $power_coupling_ROHM, $power_eddy_ROHM, $power_IS_coupling, $power_hyst_ROHF, $power_eddy_ROHF, $power_ohmic},
                            Format "%g %14.12e %14.12e %14.12e %14.12e %14.12e %14.12e %14.12e %14.12e %14.12e", File outputPowerFull];
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
                    {% if dm.magnet.solve.rohm.enable %}
                    RemoveLastSolution[B_OR_H];
                    {% endif %}
                    {% if dm.magnet.solve.rohf.enable %}
                    RemoveLastSolution[FLUX];
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
            DeleteFile[pcrossingFile];
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
    { Name MagDyn_hphi; NameOfFormulation MagDyn_hphi;
        Quantity {
            // ----------------------------
            // ------- LOCAL fields -------
            // ----------------------------
            { Name phi; Value{ Local{ [ {dInv h} ] ;
                In OmegaCC; Jacobian Vol; } } }
            { Name h; Value{ Local{ [ {h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name k; Value{ Local{ [ {k_IS} ] ;
                In OmegaC; Jacobian Vol; } } }
            { Name j; Value{ Local{ [ {d h} ] ;
                In OmegaC; Jacobian Vol; } } }
            { Name jz; Value{ Local{ [ CompZ[{d h}] ] ;
                In OmegaC; Jacobian Vol; } } }
            { Name b; Value {
                Term { [ mu[] * {h} ] ; In MagnLinDomain; Jacobian Vol; }
                {% if dm.magnet.solve.rohm.enable %}
                Term { [ {b} ] ; In MagnHystDomain; Jacobian Vol; }
                {% else %}
                Term { [ mu[] * {h} ] ; In MagnHystDomain; Jacobian Vol; }
                {% endif %}
                {% if dm.magnet.solve.formulation_parameters.hphia %}
                Term { [ {d a} ] ; In Omega_a; Jacobian Vol; }
                {% endif %}
                }
            }
            { Name hsVal; Value{ Term { [ hsVal[] ]; In Omega; } } }
            {% if dm.magnet.solve.rohf.enable %}
            { Name flux; Value{ Local{ [ {flux} ] ; 
                In MagnHystDomain; Jacobian Vol; } } }
            {% endif %} 
            {% if dm.magnet.solve.rohm.enable %}
            { Name m; Value{ Local{ [ {b} - mu0*{h} ] ;
                In MagnHystDomain; Jacobian Vol; } } }
            {% endif %} 
            {% if dm.magnet.solve.formulation_parameters.hphia %}
            { Name a; Value{ Local{ [ {a} ] ;
                In Omega; Jacobian Vol; } } }
            {% endif %}         
            // ----------------------------
            // ----- GLOBAL quantities ----
            // ----------------------------
            { Name I; Value { Term{ [ {I} ] ; In Cuts; } } }
            { Name V; Value { Term{ [ {V} ] ; In Cuts; } } }
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            { Name Ip; Value { Term{ [ {Ip} ] ; In PoweringCircuit; } } }
            { Name Vp; Value { Term{ [ {Vp} ] ; In PoweringCircuit; } } }
            {% endif %}
            { Name magnetization; Value{ Integral{ [ 0.5 * XYZ[] /\ {d h} ] ;
                In OmegaC; Integration Int; Jacobian Vol; } } } // Magnetization from current density only (does not include effects from ROHM)
            // ----------------------------
            // ----- POWER quantities -----
            // ----------------------------
            // NB: (h+h[1])/2 instead of h -> to avoid a constant sign error accumulation
            { Name power_tot_with_stored_energy_change; // WARNING: contains stored energy change! -> not only pure loss, so can be negative. Useful for convergence criterion
                Value{
                    // DISCC model, IS coupling currents
                    Integral{ [ (sigma_IS[] * {k_IS}) * {k_IS}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% if dm.magnet.solve.rohm.enable %}
                    // ROHM model (contains stored energy change! -> not only pure loss)
                    Integral{ [ (bhyst[{h},{% for i in range(1, 1+len(mp.rohm['alpha'])) %} {hrev_<<i>>}[1], {g_<<i>>}[1],{% endfor %} Norm[{b}]] - {b}[1]) / $DTime * ({h}+{h}[1])/2 ] ;
                        In MagnHystDomain ; Integration Int ; Jacobian Vol; }
                    {% endif %}
                    {% if dm.magnet.solve.rohf.enable %}
                    // ROHF model (contains stored energy change! -> not only pure loss)
                    Integral{ [ ({flux} - {flux}[1]) / $DTime * ({d h}+{d h}[1])/2 ] ;
                        In MagnHystDomain ; Integration Int ; Jacobian Vol; }
                    {% endif %}
                    {% if dm.magnet.solve.general_parameters.superconductor_linear %}
                    // Joule loss from linear Ohm's law
                    Integral{ [rho[] * {d h} * {d h}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% else %}
                    // Joule loss from current sharing (CS)
                    Integral{ [e_joule[{d h}] * {d h}] ; 
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% endif %}
                }
            }
            { Name power_tot; // Only the lossy contributions (should always be positive)
                Value{
                    // DISCC model, IS coupling currents
                    Integral{ [ (sigma_IS[] * {k_IS}) * {k_IS}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% if dm.magnet.solve.rohm.enable %}
                    // ROHM - Hyst uncoupled and eddy
                    For k In {1:N_rohm}
                        Integral { [ 0.5 * ({h} - {g~{k}} + {h}[1] - {g~{k}}[1]) * w_rohm~{k} * mu0 * Dt[{hrev~{k}}] ] ;
                            In MagnHystDomain; Integration Int ; Jacobian Vol; }
                        Integral { [ w_rohm~{k} * tau_e_rohm~{k} * mu0 * SquNorm[Dt[{hrev~{k}}]] ] ;
                            In MagnHystDomain ; Integration Int ; Jacobian Vol; }
                    EndFor
                    // ROHM - Hyst coupled and IF coupling
                    For k In {2:N_rohm}
                        Integral { [ hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}] * w_rohm~{k} * (mu0 * Dt[{hrev~{k}}] - mu0 * hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]/tau_c_rohm~{k}) ] ;
                            In MagnHystDomain ; Integration Int ; Jacobian Vol; }
                        Integral { [ mu0 * SquNorm[hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]]/tau_c_rohm~{k} * w_rohm~{k} ] ;
                            In MagnHystDomain ; Integration Int ; Jacobian Vol; }
                    EndFor
                    {% endif %}
                    {% if dm.magnet.solve.rohf.enable %}
                    // ROHF - Hyst and eddy
                    For k In {1:N_rohf}
                        Integral { [ 0.5 * ({d h} - {jreveddy~{k}} + {d h}[1] - {jreveddy~{k}}[1]) * w_rohf~{k} * Lint0 * Dt[{jrev~{k}}] ] ;
                            In MagnHystDomain ; Integration Int ; Jacobian Vol; }
                        Integral { [ w_rohf~{k} * tau_e_rohf~{k} * Lint0 * SquNorm[Dt[{jrev~{k}}]] ] ;
                            In MagnHystDomain ; Integration Int ; Jacobian Vol; }
                    EndFor
                    {% endif %}
                    {% if dm.magnet.solve.general_parameters.superconductor_linear %}
                    // Joule loss from linear Ohm's law
                    Integral{ [rho[] * {d h} * {d h}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% else %}
                    // Joule loss from current sharing (CS)
                    Integral{ [e_joule[{d h}] * {d h}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% endif %}
                }
            }
            { Name power_tot_local;
                Value{
                    {% if dm.magnet.solve.rohm.enable %}
                    // ROHM - Hyst uncoupled and eddy
                    For k In {1:N_rohm}
                        Term { [ 0.5 * ({h} - {g~{k}} + {h}[1] - {g~{k}}[1]) * w_rohm~{k} * mu0 * Dt[{hrev~{k}}] ] ;
                            In MagnHystDomain; Jacobian Vol; }
                        Term { [ w_rohm~{k} * tau_e_rohm~{k} * mu0 * SquNorm[Dt[{hrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol; } 
                    EndFor
                    // ROHM - Hyst coupled and IF coupling
                    For k In {2:N_rohm}
                        Term { [ hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}] * w_rohm~{k} * (mu0 * Dt[{hrev~{k}}] - mu0 * hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]/tau_c_rohm~{k}) ] ;
                            In MagnHystDomain ; Jacobian Vol; } 
                        Term { [ mu0 * SquNorm[hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]]/tau_c_rohm~{k} * w_rohm~{k} ] ;
                            In MagnHystDomain ; Jacobian Vol; } 
                    EndFor
                    {% endif %}
                    {% if dm.magnet.solve.rohf.enable %}
                    // ROHF - Hyst and eddy
                    For k In {1:N_rohf}
                        Term { [ 0.5 * ({d h} - {jreveddy~{k}} + {d h}[1] - {jreveddy~{k}}[1]) * w_rohf~{k} * Lint0 * Dt[{jrev~{k}}] ] ;
                            In MagnHystDomain ; Jacobian Vol;} 
                        Term { [ w_rohf~{k} * tau_e_rohf~{k} * Lint0 * SquNorm[Dt[{jrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol;} 
                    EndFor
                    {% endif %}
                    {% if dm.magnet.solve.general_parameters.superconductor_linear %}
                    // Joule loss from linear Ohm's law
                    Term{ [rho[] * {d h} * {d h}] ;
                        In OmegaC ; Jacobian Vol; }
                    {% else %}
                    // Joule loss from current sharing (CS)
                    Term{ [e_joule[{d h}] * {d h}] ;
                        In OmegaC ; Jacobian Vol; }
                    {% endif %}
                    // DISCC model, IS coupling currents
                    Term{ [ (sigma_IS[] * {k_IS}) * {k_IS}] ;
                    In OmegaC ; Jacobian Vol; }

                }
            }
            // ----- DISCC related power quantity -----
            { Name power_IS_coupling;
                Value{
                    Integral{ [ (sigma_IS[] * {k_IS}) * {k_IS}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                }
            }
            {% if dm.magnet.solve.rohm.enable %}
            // ----- ROHM related power quantities -----
            { Name power_hyst_ROHM;
                Value{
                    For k In {1:N_rohm}
                        Integral { [ 0.5 * ({h} - {g~{k}} + {h}[1] - {g~{k}}[1]) * w_rohm~{k} * mu0 * Dt[{hrev~{k}}] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_eddy_ROHM;
                Value{
                    For k In {1:N_rohm}
                        Integral { [ w_rohm~{k} * tau_e_rohm~{k} * mu0 * SquNorm[Dt[{hrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_coupling_ROHM;
                Value{
                    For k In {2:N_rohm} // starts at k=2 to avoid division by 0 in the first cell, coupling time constant MUST indeed be zero for the first cell for this to make sense
                        Integral { [ mu0 * SquNorm[hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]]/tau_c_rohm~{k} * w_rohm~{k} ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_hyst_c_ROHM;
                Value{
                    For k In {2:N_rohm} // starts at k=2 to avoid division by 0 in the first cell, coupling time constant MUST indeed be zero for the first cell for this to make sense
                        Integral { [ hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}] * w_rohm~{k} * (mu0 * Dt[{hrev~{k}}] - mu0 * hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]/tau_c_rohm~{k}) ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_tot_local_ROHM;
                Value{
                    For k In {1:N_rohm}
                        Term { [ 0.5 * ({h} - {g~{k}} + {h}[1] - {g~{k}}[1]) * w_rohm~{k} * mu0 * Dt[{hrev~{k}}] ] ;
                            In MagnHystDomain; Jacobian Vol; }
                        Term { [ w_rohm~{k} * tau_e_rohm~{k} * mu0 * SquNorm[Dt[{hrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol; } 
                    EndFor
                    For k In {2:N_rohm} // starts at k=2 to avoid division by 0 in the first cell, coupling time constant MUST indeed be zero for the first cell for this to make sense
                        Term { [ hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}] * w_rohm~{k} * (mu0 * Dt[{hrev~{k}}] - mu0 * hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]/tau_c_rohm~{k}) ] ;
                            In MagnHystDomain ; Jacobian Vol; } 
                        Term { [ mu0 * SquNorm[hcoupling[mu0*Dt[{hrev~{k}}], Norm[mu0*{hrev~{k}}], tau_c_rohm~{k}, chi_rohm~{k}]]/tau_c_rohm~{k} * w_rohm~{k} ] ;
                            In MagnHystDomain ; Jacobian Vol; } 
                    EndFor
                }
            }
            {% endif %}
            {% if dm.magnet.solve.rohf.enable %}
            // ----- ROHM related power quantities -----
            { Name power_hyst_ROHF;
                Value{
                    For k In {1:N_rohf}
                        Integral { [ 0.5 * ({d h} - {jreveddy~{k}} + {d h}[1] - {jreveddy~{k}}[1]) * w_rohf~{k} * Lint0 * Dt[{jrev~{k}}] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_eddy_ROHF;
                Value{
                    For k In {1:N_rohf}
                        Integral { [ w_rohf~{k} * tau_e_rohf~{k} * Lint0 * SquNorm[Dt[{jrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol; Integration Int; } 
                    EndFor
                }
            }
            { Name power_total_local_ROHF;
                Value{
                    For k In {1:N_rohf}
                        Term { [ 0.5 * ({d h} - {jreveddy~{k}} + {d h}[1] - {jreveddy~{k}}[1]) * w_rohf~{k} * Lint0 * Dt[{jrev~{k}}] ] ;
                            In MagnHystDomain ; Jacobian Vol;} 
                        Term { [ w_rohf~{k} * tau_e_rohf~{k} * Lint0 * SquNorm[Dt[{jrev~{k}}]] ] ;
                            In MagnHystDomain ; Jacobian Vol;} 
                    EndFor
                }
            }
            {% endif %}
            // ----- Joule power quantities -----
            { Name power_ohmic;
                Value{
                    {% if dm.magnet.solve.general_parameters.superconductor_linear %}
                    Integral{ [rho[] * {d h} * {d h}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% else %}
                    Integral{ [e_joule[{d h}] * {d h}] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                    {% endif %}
                }
            }
            { Name power_local_ohmic;
                Value{
                    {% if dm.magnet.solve.general_parameters.superconductor_linear %}
                    Term{ [rho[] * {d h} * {d h}] ;
                        In OmegaC ; Jacobian Vol; }
                    {% else %}
                    Term{ [e_joule[{d h}] * {d h}] ;
                        In OmegaC ; Jacobian Vol; }
                    {% endif %}
                }
            }
        }
    }
    { Name MagDyn_hphi_freq; NameOfFormulation MagDyn_hphi_freq;
        Quantity { 
            { Name phi; Value{ Local{ [ {dInv h} ] ;
                In OmegaCC; Jacobian Vol; } } }
            { Name h; Value{ Local{ [ {h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name k; Value{ Local{ [ {k_IS} ] ;
                In OmegaC; Jacobian Vol; } } }
            { Name b; Value { Local { [ mu[] * {h} ] ; 
                In MagnLinDomain; Jacobian Vol; } } }
            { Name j; Value{ Local{ [ {d h} ] ;
                In Omega; Jacobian Vol; } } }
            { Name jz; Value{ Local{ [ CompZ[{d h}] ] ;
                In Omega; Jacobian Vol; } } }
            { Name power_crossing;
                Value{ 
                    Local{ [0.5 * (sigma_IS[] * {k_IS}) * Conj[{k_IS}]] ;
                        In OmegaC ; Jacobian Vol; }
                }
            }
            { Name total_power_crossing;
                Value{
                    Integral{ [0.5 * (sigma_IS[] * {k_IS}) * Conj[{k_IS}]] ;
                        In OmegaC ; Integration Int ; Jacobian Vol; }
                }
            }
            { Name I; Value { Term{ [ {I} ] ; In Cuts; } } }
            { Name V; Value { Term{ [ {V} ] ; In Cuts; } } }
        }
    }
}
PostOperation {
    { Name MagDyn;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            // Local field solutions
            {% if dm.magnet.postproc.generate_pos_files %}
            Print[ j, OnElementsOf Cables , File StrCat["js.pos"], Name "js [A/m2]" ];
            Print[ k, OnElementsOf Cables , File StrCat["k.pos"], Name "k [V]" ];
            Print[ b, OnElementsOf Omega , File StrCat["b.pos"], Name "b [T]" ];
            //Print[ h, OnElementsOf Omega , File StrCat["h.pos"], Name "h [A/m]" ];
            Print[ power_tot_local, OnElementsOf Cables , File StrCat["p_tot.pos"], Name "p_tot [W/m3]" ];
            {% if dm.magnet.solve.rohm.enable %}
            Print[ m, OnElementsOf Cables , File StrCat["m.pos"], Name "m [T]" ];
            {% endif %}
            {% if dm.magnet.solve.rohf.enable %}
            // Print[ flux, OnElementsOf MagnHystDomain , File StrCat["flux_ROHF.pos"], Name "flux_ROHF [Wb/m]" ];
            {% endif %}
            {% endif %}
            // Global solutions
            Print[ I, OnRegion Cuts, File StrCat[resDirectory, "/It.txt"], Format SimpleTable];        
            Print[ V, OnRegion Cuts, File StrCat[resDirectory, "/Vt.txt"], Format SimpleTable]; 
            {% if dm.magnet.solve.source_parameters.parallel_resistor %}
            Print[ Ip, OnRegion PoweringCircuit, File StrCat[resDirectory,"/Ip.txt"], Format SimpleTable];
            Print[ Vp, OnRegion PoweringCircuit, File StrCat[resDirectory,"/Vp.txt"], Format SimpleTable];
            {% endif %}
            {% if dm.magnet.postproc.save_last_magnetic_field != "None" %}
            // Last magnetic field solution for projection. Note the special format GmshParsed required for proper GmshRead[] operation in the later pre-resolution.
            Print[ h, OnElementsOf Omega, Format GmshParsed , File StrCat["../", "<<dm.magnet.postproc.save_last_magnetic_field>>", ".pos"], Name "h [A/m]", LastTimeStepOnly ];
            {% endif %}
            {% for i in range(0, len(rm.powered.Cables.vol.numbers)) %}
            Print[ power_tot[Cable_<<i+1>>], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_cable_<<i+1>>.txt"] ];
            {% endfor %}

            // Print[ power_tot[Omega], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_tot.txt"] ];
            // Print[ power_IS_coupling[Omega], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_IS.txt"] ];
            // {% if dm.magnet.solve.rohm.enable %}
            // Print[ power_hyst_ROHM[Cables], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_hyst_ROHM.txt"]];  
            // Print[ power_eddy_ROHM[Cables], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_eddy_ROHM.txt"]];
            // Print[ power_hyst_c_ROHM[Cables], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_hyst_c_ROHM.txt"]];             
            // Print[ power_coupling_ROHM[Cables], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_coupling_ROHM.txt"]];
            // {% endif %}
            // {% if dm.magnet.solve.rohf.enable %}
            // Print[ power_hyst_ROHF[Omega], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_hyst_ROHF.txt"]];
            // Print[ power_eddy_ROHF[Omega], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_eddy_ROHF.txt"]];
            // {% endif %}
            // Print[ power_ohmic[Omega], OnGlobal, Format TimeTable, File StrCat[resDirectory,"/power_ohmic.txt"]];
        }
    }
    { Name MagDyn_energy; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ power_tot_with_stored_energy_change[Omega], OnGlobal, Format Table, StoreInVariable $indicLoss, File StrCat[resDirectory,"/dummy.txt"] ];
        }
    }
    { Name MagDyn_energy_full; LastTimeStepOnly 1 ;
        NameOfPostProcessing MagDyn_hphi;
        Operation {
            Print[ power_tot[Omega],            OnGlobal, Format Table, StoreInVariable $power_tot, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_IS_coupling[Omega],    OnGlobal, Format Table, StoreInVariable $power_IS_coupling, File StrCat[resDirectory,"/dummy.txt"] ];
            {% if dm.magnet.solve.rohm.enable %}
            Print[ power_hyst_ROHM[Omega],      OnGlobal, Format Table, StoreInVariable $power_hyst_ROHM, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_eddy_ROHM[Omega],      OnGlobal, Format Table, StoreInVariable $power_eddy_ROHM, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_hyst_c_ROHM[Omega],    OnGlobal, Format Table, StoreInVariable $power_hyst_c_ROHM, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_coupling_ROHM[Omega],  OnGlobal, Format Table, StoreInVariable $power_coupling_ROHM, File StrCat[resDirectory,"/dummy.txt"] ];
            {% endif %}
            {% if dm.magnet.solve.rohf.enable %}
            Print[ power_hyst_ROHF[Omega],      OnGlobal, Format Table, StoreInVariable $power_hyst_ROHF, File StrCat[resDirectory,"/dummy.txt"] ];
            Print[ power_eddy_ROHF[Omega],      OnGlobal, Format Table, StoreInVariable $power_eddy_ROHF, File StrCat[resDirectory,"/dummy.txt"] ];   
            {% endif %}
            Print[ power_ohmic[Omega],          OnGlobal, Format Table, StoreInVariable $power_ohmic, File StrCat[resDirectory,"/dummy.txt"] ];
        }
    }
}
