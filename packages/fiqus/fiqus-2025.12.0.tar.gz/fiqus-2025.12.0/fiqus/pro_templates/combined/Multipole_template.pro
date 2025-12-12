Include "<<BHcurves>>";
{% import "materials.pro" as materials %}
{% import "TSA_materials.pro" as TSA_materials %}

{% macro criticalCurrentDensity(region_name, cond, time_trigger, cond_name) %}
{% if cond.Jc_fit.type == 'CUDI1' %}
  {% if cond.strand.type == 'Round' %}
    {% set wire_diameter = (cond.cable.n_strands)**(1/2) * cond.strand.diameter %}
  {% elif cond.strand.type == 'Rectangular' %}
    {% set n_strands = cond.cable.n_strands if cond.cable.type == 'Rutherford' else 1 %}
    {% set wire_diameter = (4 * n_strands * cond.strand.bare_width * cond.strand.bare_height / Pi) ** (1 / 2) %}
  {% endif %}
  criticalCurrentDensity[<<region_name>>] = $Time > <<time_trigger>>? 0: <<materials[criticalCurrentDensityMacroName[cond.strand.material_superconductor + '_' + cond.Jc_fit.type]](C1=cond.Jc_fit.C1_CUDI1, C2=cond.Jc_fit.C2_CUDI1, Tc0=cond.Jc_fit.Tc0_CUDI1, Bc20=cond.Jc_fit.Bc20_CUDI1, wireDiameter=wire_diameter, Cu_noCu=cond.strand.Cu_noCu_in_strand)>> * f_sc_<<cond_name>>;
{% elif cond.Jc_fit.type == 'Summers' %}
  criticalCurrentDensity[<<region_name>>] = $Time > <<time_trigger>>? 0: <<materials[criticalCurrentDensityMacroName[cond.strand.material_superconductor + '_' + cond.Jc_fit.type]](Jc0=cond.Jc_fit.Jc0_Summers, Tc0=cond.Jc_fit.Tc0_Summers, Bc20=cond.Jc_fit.Bc20_Summers)>> * f_sc_<<cond_name>>;
{% elif cond.Jc_fit.type == 'Bordini' %}
  criticalCurrentDensity[<<region_name>>] = $Time > <<time_trigger>>? 0: <<materials[criticalCurrentDensityMacroName[cond.strand.material_superconductor + '_' + cond.Jc_fit.type]](Tc0=cond.Jc_fit.Tc0_Bordini, Bc20=cond.Jc_fit.Bc20_Bordini, C0=cond.Jc_fit.C0_Bordini, alpha=cond.Jc_fit.alpha_Bordini)>> * f_sc_<<cond_name>>;
{% elif cond.Jc_fit.type == 'BSCCO_2212_LBNL' %}
  criticalCurrentDensity[<<region_name>>] = $Time > <<time_trigger>>? 0: <<materials[criticalCurrentDensityMacroName[cond.strand.material_superconductor + '_' + cond.Jc_fit.type]](f_scaling=cond.Jc_fit.f_scaling_Jc_BSCCO2212)>>  * f_sc_<<cond_name>>;
{% endif %}
{% endmacro %}

{% if dm.magnet.solve.thermal.solve_type %}

    stop_temperature = <<dm.magnet.solve.thermal.time_stepping.stop_temperature>>;
    /* -------------------------------------------------------------------------- */
    {% if dm.magnet.geometry.thermal.use_TSA %}
    // Checkered support indexing for bare part
    // first index: neighboring information in azimuthal direction
    // second index: neighboring information in radial direction
    {% if dm.magnet.geometry.thermal.with_wedges %}
      {% set bare_1_1 = rm_TH.powered['r1_a1'].vol.numbers + rm_TH.induced['r1_a1'].vol.numbers %}
      {% set bare_2_1 = rm_TH.powered['r2_a1'].vol.numbers + rm_TH.induced['r2_a1'].vol.numbers %}
      {% set bare_1_2 = rm_TH.powered['r1_a2'].vol.numbers + rm_TH.induced['r1_a2'].vol.numbers %}
      {% set bare_2_2 = rm_TH.powered['r2_a2'].vol.numbers + rm_TH.induced['r2_a2'].vol.numbers %}
    {% else %}
      {% set bare_1_1 = rm_TH.powered['r1_a1'].vol.numbers %}
      {% set bare_2_1 = rm_TH.powered['r2_a1'].vol.numbers %}
      {% set bare_1_2 = rm_TH.powered['r1_a2'].vol.numbers %}
      {% set bare_2_2 = rm_TH.powered['r2_a2'].vol.numbers %}
    {% endif %}

    bare_1_1 = {<<bare_1_1|join(', ')>>};
    bare_2_1 = {<<bare_2_1|join(', ')>>};
    bare_1_2 = {<<bare_1_2|join(', ')>>};
    bare_2_2 = {<<bare_2_2|join(', ')>>};

    // Shell lines belonging to the bare parts as indexed above
    {% if dm.magnet.geometry.thermal.with_wedges %}
      {% set bare_layers_1_1 = rm_TH.powered['r1_a1'].surf_in.numbers  +  rm_TH.induced['r1_a1'].surf_in.numbers %}
      {% set bare_layers_2_1 = rm_TH.powered['r2_a1'].surf_in.numbers  +  rm_TH.induced['r2_a1'].surf_in.numbers %}
      {% set bare_layers_1_2 = rm_TH.powered['r1_a2'].surf_in.numbers  +  rm_TH.induced['r1_a2'].surf_in.numbers %}
      {% set bare_layers_2_2 = rm_TH.powered['r2_a2'].surf_in.numbers  +  rm_TH.induced['r2_a2'].surf_in.numbers %}
    {% else %}
      {% set bare_layers_1_1 = rm_TH.powered['r1_a1'].surf_in.numbers %}
      {% set bare_layers_2_1 = rm_TH.powered['r2_a1'].surf_in.numbers %}
      {% set bare_layers_1_2 = rm_TH.powered['r1_a2'].surf_in.numbers %}
      {% set bare_layers_2_2 = rm_TH.powered['r2_a2'].surf_in.numbers %}
    {% endif %}

    bare_layers_1_1() = {<<bare_layers_1_1|join(', ')>>};
    bare_layers_2_1() = {<<bare_layers_2_1|join(', ')>>};
    bare_layers_1_2() = {<<bare_layers_1_2|join(', ')>>};
    bare_layers_2_2() = {<<bare_layers_2_2|join(', ')>>};

    // ------------ BOUNDARY CONDITIONS --------------------------------------------
    // boundary shells where Dirichlet BC applied, there we need two Tdisc
    // indexing follows the one with the bares BUT we have to think of these lines
    // as neighbors belonging to the non-existing exterior bare part, i.e.,
    // the line touching bare_2_1 will then be bare_1_1
    bndDir_1_1() = {<<rm_TH.boundaries.thermal.temperature.groups['r1_a1']|join(', ')>>};
    bndDir_2_1() = {<<rm_TH.boundaries.thermal.temperature.groups['r2_a1']|join(', ')>>};
    bndDir_1_2() = {<<rm_TH.boundaries.thermal.temperature.groups['r1_a2']|join(', ')>>};
    bndDir_2_2() = {<<rm_TH.boundaries.thermal.temperature.groups['r2_a2']|join(', ')>>};

    // boundary shells where Neumann BC applied, there we need two Tdisc
    // indexing follows the one with the bares BUT we have to think of these lines
    // as neighbors belonging to the non-existing exterior bare part, i.e.,
    // the line touching bare_2_1 will then be bare_1_1
    bndNeu_1_1() = {<<rm_TH.boundaries.thermal.heat_flux.groups['r1_a1']|join(', ')>>};
    bndNeu_2_1() = {<<rm_TH.boundaries.thermal.heat_flux.groups['r2_a1']|join(', ')>>};
    bndNeu_1_2() = {<<rm_TH.boundaries.thermal.heat_flux.groups['r1_a2']|join(', ')>>};
    bndNeu_2_2() = {<<rm_TH.boundaries.thermal.heat_flux.groups['r2_a2']|join(', ')>>};

    // boundary shells where Robin BC applied, follows the same indexing scheme as
    // Dirichlet, i.e.,
    // indexing follows the one with the bares BUT we have to think of these lines
    // as neighbors belonging to the non-existing exterior bare part, i.e.,
    // the line touching bare_2_1 will then be bare_1_1
    bndRobin_1_1() = { <<rm_TH.boundaries.thermal.cooling.groups['r1_a1']|join(', ')>>};
    bndRobin_2_1() = { <<rm_TH.boundaries.thermal.cooling.groups['r2_a1']|join(', ')>>};
    bndRobin_1_2() = { <<rm_TH.boundaries.thermal.cooling.groups['r1_a2']|join(', ')>>};
    bndRobin_2_2() = { <<rm_TH.boundaries.thermal.cooling.groups['r2_a2']|join(', ')>>};

    // for Robin and Neumann, we also need to store some information for GetDP to know the
    // outer virtual shell element
    // first index: same as first index of horVer_layers of Robin (simplified) or midLayers (non-simplified)
    // second index: same as first index of bndRobin or bndNeumann
    // third index: same as second index of bndRobin or bndNeumann
    {% set bndRobinInt_1_1_1 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r1_a1']).intersection(bare_layers_2_1)) %}
    {% set bndRobinInt_2_1_1 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r1_a1']).intersection(bare_layers_1_2)) %}

    {% set bndRobinInt_1_2_1 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r2_a1']).intersection(bare_layers_1_1)) %}
    {% set bndRobinInt_2_2_1 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r2_a1']).intersection(bare_layers_2_2)) %}

    {% set bndRobinInt_1_1_2 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r1_a2']).intersection(bare_layers_2_2)) %}
    {% set bndRobinInt_2_1_2 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r1_a2']).intersection(bare_layers_1_1)) %}

    {% set bndRobinInt_1_2_2 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r2_a2']).intersection(bare_layers_1_2)) %}
    {% set bndRobinInt_2_2_2 =  list(set(rm_TH.boundaries.thermal.cooling.groups['r2_a2']).intersection(bare_layers_2_1)) %}

    // Neumann
    {% set bndNeuInt_1_1_1 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r1_a1']).intersection(bare_layers_2_1)) %}
    {% set bndNeuInt_2_1_1 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r1_a1']).intersection(bare_layers_1_2)) %}

    {% set bndNeuInt_1_2_1 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r2_a1']).intersection(bare_layers_1_1)) %}
    {% set bndNeuInt_2_2_1 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r2_a1']).intersection(bare_layers_2_2)) %}

    {% set bndNeuInt_1_1_2 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r1_a2']).intersection(bare_layers_2_2)) %}
    {% set bndNeuInt_2_1_2 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r1_a2']).intersection(bare_layers_1_1)) %}

    {% set bndNeuInt_1_2_2 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r2_a2']).intersection(bare_layers_1_2)) %}
    {% set bndNeuInt_2_2_2 =  list(set(rm_TH.boundaries.thermal.heat_flux.groups['r2_a2']).intersection(bare_layers_2_1)) %}

    // QH
    {% set ns = namespace(all_QH=[]) %}

    {% for taglist in rm_TH.thin_shells.quench_heaters.thin_shells %}
        {% set ns.all_QH = ns.all_QH + taglist %}
    {% endfor %}

    {% set QH_1_1 = set(ns.all_QH).intersection(set(bare_layers_2_1).intersection(rm_TH.thin_shells.normals_directed['azimuthally']).union(set(bare_layers_1_2).intersection(rm_TH.thin_shells.normals_directed['radially'])))  %}
    {% set QH_2_1 = set(ns.all_QH).intersection(set(bare_layers_1_1).intersection(rm_TH.thin_shells.normals_directed['azimuthally']).union(set(bare_layers_2_2).intersection(rm_TH.thin_shells.normals_directed['radially'])))  %}
    {% set QH_1_2 = set(ns.all_QH).intersection(set(bare_layers_2_2).intersection(rm_TH.thin_shells.normals_directed['azimuthally']).union(set(bare_layers_1_1).intersection(rm_TH.thin_shells.normals_directed['radially'])))  %}
    {% set QH_2_2 = set(ns.all_QH).intersection(set(bare_layers_1_2).intersection(rm_TH.thin_shells.normals_directed['azimuthally']).union(set(bare_layers_2_1).intersection(rm_TH.thin_shells.normals_directed['radially'])))  %}
    QH_1_1() = {<<QH_1_1|join(', ')>>};
    QH_2_1() = {<<QH_2_1|join(', ')>>};

    QH_1_2() = {<<QH_1_2|join(', ')>>};
    QH_2_2() = {<<QH_2_2|join(', ')>>};

    // midLayers
    {% if dm.magnet.geometry.thermal.with_wedges %}
      {% set midLayers_1_1 = rm_TH.powered['r1_a1'].surf_out.numbers  +  rm_TH.induced['r1_a1'].surf_out.numbers %}
      {% set midLayers_2_1 = rm_TH.powered['r2_a1'].surf_out.numbers  +  rm_TH.induced['r2_a1'].surf_out.numbers %}
      {% set midLayers_1_2 = rm_TH.powered['r1_a2'].surf_out.numbers  +  rm_TH.induced['r1_a2'].surf_out.numbers %}
      {% set midLayers_2_2 = rm_TH.powered['r2_a2'].surf_out.numbers  +  rm_TH.induced['r2_a2'].surf_out.numbers %}
    {% else %}
      {% set midLayers_1_1 = rm_TH.powered['r1_a1'].surf_out.numbers %}
      {% set midLayers_2_1 = rm_TH.powered['r2_a1'].surf_out.numbers %}
      {% set midLayers_1_2 = rm_TH.powered['r1_a2'].surf_out.numbers %}
      {% set midLayers_2_2 = rm_TH.powered['r2_a2'].surf_out.numbers %}
    {% endif %}
    midLayers_1_1() = {<<midLayers_1_1|join(', ')>>};
    midLayers_2_1() = {<<midLayers_2_1|join(', ')>>};
    midLayers_1_2() = {<<midLayers_1_2|join(', ')>>};
    midLayers_2_2() = {<<midLayers_2_2|join(', ')>>};
    midLayers() = {<<rm_TH.thin_shells.mid_turns_layers_poles|join(', ')>>};

    {# midLayers_1: oriented along radial direction, connecting half-turns and poles #}
    {# part of the vertical and horizontal splitting #}
    {# it needs to match the definition of the function spaces for identifying plus and minus side correctly #}
    {% set midLayers_1 = list(set(rm_TH.thin_shells.normals_directed['azimuthally']).intersection(rm_TH.thin_shells.mid_turns_layers_poles)) %}
    {# midLayers_2: oriented along azimuth direction, connecting layer # }
    {# part of the vertical and horizontal splitting #}
    {% set midLayers_2 = list(set(rm_TH.thin_shells.normals_directed['radially']).intersection(rm_TH.thin_shells.mid_turns_layers_poles)) %}

    // AUX GROUPS ------------------------------------------------------------------
    allLayers = {{% if rm_TH.powered['r1_a1'].surf_in.numbers %}<<rm_TH.powered['r1_a1'].surf_in.numbers|join(', ')>>{% endif %}
                 {% if rm_TH.powered['r2_a1'].surf_in.numbers %}, <<rm_TH.powered['r2_a1'].surf_in.numbers|join(', ')>>{% endif %}
                 {% if rm_TH.powered['r1_a2'].surf_in.numbers %}, <<rm_TH.powered['r1_a2'].surf_in.numbers|join(', ')>>{% endif %}
                 {% if rm_TH.powered['r2_a2'].surf_in.numbers %}, <<rm_TH.powered['r2_a2'].surf_in.numbers|join(', ')>>{% endif %}
                 {% if dm.magnet.geometry.thermal.with_wedges %}
                 {% if rm_TH.induced['r1_a1'].surf_in.numbers %}, <<rm_TH.induced['r1_a1'].surf_in.numbers|join(', ')>>{% endif %}
                 {% if rm_TH.induced['r2_a1'].surf_in.numbers %}, <<rm_TH.induced['r2_a1'].surf_in.numbers|join(', ')>>{% endif %}
                 {% if rm_TH.induced['r1_a2'].surf_in.numbers %}, <<rm_TH.induced['r1_a2'].surf_in.numbers|join(', ')>>{% endif %}
                 {% if rm_TH.induced['r2_a2'].surf_in.numbers %}, <<rm_TH.induced['r2_a2'].surf_in.numbers|join(', ')>>{% endif %}
                 {% endif %}};
    {% endif %}

{% endif %}

Group {
{% if dm.magnet.solve.electromagnetics.solve_type %}

      <<rm_EM.air.vol.name>> = Region[ <<rm_EM.air.vol.number>> ];  // Air
      <<rm_EM.air_far_field.vol.names[0]>> = Region[ <<rm_EM.air_far_field.vol.numbers[0]>> ];  // AirInf
    {% for name, number in zip(rm_EM.powered['r1_a1'].vol.names, rm_EM.powered['r1_a1'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
    {% for name, number in zip(rm_EM.powered['r2_a1'].vol.names, rm_EM.powered['r2_a1'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
    {% for name, number in zip(rm_EM.powered['r1_a2'].vol.names, rm_EM.powered['r1_a2'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
    {% for name, number in zip(rm_EM.powered['r2_a2'].vol.names, rm_EM.powered['r2_a2'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}

    {% if dm.magnet.geometry.electromagnetics.with_wedges %}
      {% for name, number in zip(rm_EM.induced['r1_a1'].vol.names, rm_EM.induced['r1_a1'].vol.numbers) %}
        <<name>> = Region[ <<number>> ];
      {% endfor %}
      {% for name, number in zip(rm_EM.induced['r2_a1'].vol.names, rm_EM.induced['r2_a1'].vol.numbers) %}
        <<name>> = Region[ <<number>> ];
      {% endfor %}
      {% for name, number in zip(rm_EM.induced['r1_a2'].vol.names, rm_EM.induced['r1_a2'].vol.numbers) %}
        <<name>> = Region[ <<number>> ];
      {% endfor %}
      {% for name, number in zip(rm_EM.induced['r2_a2'].vol.names, rm_EM.induced['r2_a2'].vol.numbers) %}
        <<name>> = Region[ <<number>> ];
      {% endfor %}
    {% endif %}

    {% if dm.magnet.geometry.electromagnetics.with_iron_yoke %}
      {% for name, number in zip(rm_EM.iron_yoke.vol.names, rm_EM.iron_yoke.vol.numbers) %}
        <<name>> = Region[ <<number>> ];
      {% endfor %}
    {% endif %}

      <<rm_EM.air_far_field.surf.name>> = Region[ <<rm_EM.air_far_field.surf.number>> ];
    {% if rm_EM.boundaries.symmetry.normal_free.number %}
      <<rm_EM.boundaries.symmetry.normal_free.name>> = Region[ <<rm_EM.boundaries.symmetry.normal_free.number>> ];
    {% endif %}

      <<nc.omega>><<nc.powered>>_EM = Region[ {
                 {% if rm_EM.powered['r1_a1'].vol.names %}<<rm_EM.powered['r1_a1'].vol.names|join(', ')>>{% endif %}
                 {% if rm_EM.powered['r1_a2'].vol.names %}, <<rm_EM.powered['r1_a2'].vol.names|join(', ')>>{% endif %}
                 {% if rm_EM.powered['r2_a1'].vol.names %}, <<rm_EM.powered['r2_a1'].vol.names|join(', ')>>{% endif %}
                 {% if rm_EM.powered['r2_a2'].vol.names %}, <<rm_EM.powered['r2_a2'].vol.names|join(', ')>>{% endif %}} ];

    {% if dm.magnet.geometry.electromagnetics.with_iron_yoke %}
      <<nc.omega>><<nc.iron>>_EM = Region[ {<<rm_EM.iron_yoke.vol.names|join(', ')>>} ];
    {% endif %}

    {% if dm.magnet.geometry.electromagnetics.with_wedges %}
      <<nc.omega>><<nc.induced>>_EM = Region[ {
                 {% if rm_EM.induced['r1_a1'].vol.names %}<<rm_EM.induced['r1_a1'].vol.names|join(', ')>>{% endif %}
                 {% if rm_EM.induced['r1_a2'].vol.names %}, <<rm_EM.induced['r1_a2'].vol.names|join(', ')>>{% endif %}
                 {% if rm_EM.induced['r2_a1'].vol.names %}, <<rm_EM.induced['r2_a1'].vol.names|join(', ')>>{% endif %}
                 {% if rm_EM.induced['r2_a2'].vol.names %}, <<rm_EM.induced['r2_a2'].vol.names|join(', ')>>{% endif %}} ];
    {% endif %}

      <<nc.omega>><<nc.air_far_field>>_EM = Region[ <<rm_EM.air_far_field.vol.names[0]>> ];
      <<nc.omega>><<nc.air>>_EM = Region[ <<rm_EM.air.vol.name>> ];
      <<nc.omega>><<nc.conducting>>_EM = Region[ {<<nc.omega>><<nc.powered>>_EM{% if dm.magnet.geometry.electromagnetics.with_iron_yoke %}, <<nc.omega>><<nc.iron>>_EM{% endif %}
                    {% if dm.magnet.geometry.electromagnetics.with_wedges %}, <<nc.omega>><<nc.induced>>_EM{% endif %}} ];
      <<nc.omega>>_EM = Region[ {<<rm_EM.air.vol.name>>, <<rm_EM.air_far_field.vol.names[0]>>, <<nc.omega>><<nc.powered>>_EM{% if dm.magnet.geometry.electromagnetics.with_iron_yoke %}, <<nc.omega>><<nc.iron>>_EM{% endif %}
                    {% if dm.magnet.geometry.electromagnetics.with_wedges %}, <<nc.omega>><<nc.induced>>_EM{% endif %}} ];
      <<nc.boundary>><<nc.omega>> = Region[ {<<rm_EM.air_far_field.surf.name>>{% if rm_EM.boundaries.symmetry.normal_free.number %}, <<rm_EM.boundaries.symmetry.normal_free.name>>{% endif %}}];

{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}

  {% if dm.magnet.geometry.thermal.use_TSA %}
    // --------------------- BARE ------------------------------------------------

    // physical regions of the bare blocks
    For i In {1:2}
      For j In {1:2}
        Bare~{i}~{j} = Region[ bare~{i}~{j} ];
        <<nc.omega>>_TH     += Region[ bare~{i}~{j} ];
      EndFor
    EndFor

    // ------------------- SHELLS ------------------------------------------------
    For i In {1:2}
      For j In {1:2}
        // integration domains
        Bare_Layers~{i}~{j}  = Region[ bare_layers~{i}~{j} ];
        Bare_Layers~{i}~{j} += Region[ bndDir~{i}~{j} ];
        Bare_Layers~{i}~{j} += Region[ bndNeu~{i}~{j} ];
        Bare_Layers~{i}~{j} += Region[ bndRobin~{i}~{j} ];

        Bare_Layers~{i}~{j} += Region[ QH~{i}~{j} ];

        Domain_Insulated_Str~{i}~{j} = Region[ { Bare~{i}~{j},
          Bare_Layers~{i}~{j} } ];

        midLayers~{i}~{j} = Region[midLayers~{i}~{j}];

      EndFor
    EndFor

    midLayers = Region[midLayers];

  {% endif %}

  {% for name, number in zip(rm_TH.powered['r1_a1'].vol.names, rm_TH.powered['r1_a1'].vol.numbers) %}
    <<name>> = Region[ <<number>> ];
  {% endfor %}
  {% for name, number in zip(rm_TH.powered['r2_a1'].vol.names, rm_TH.powered['r2_a1'].vol.numbers) %}
    <<name>> = Region[ <<number>> ];
  {% endfor %}
  {% for name, number in zip(rm_TH.powered['r1_a2'].vol.names, rm_TH.powered['r1_a2'].vol.numbers) %}
    <<name>> = Region[ <<number>> ];
  {% endfor %}
  {% for name, number in zip(rm_TH.powered['r2_a2'].vol.names, rm_TH.powered['r2_a2'].vol.numbers) %}
    <<name>> = Region[ <<number>> ];
  {% endfor %}

  {% if dm.magnet.geometry.thermal.with_wedges %}
    {% for name, number in zip(rm_TH.induced['r1_a1'].vol.names, rm_TH.induced['r1_a1'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
    {% for name, number in zip(rm_TH.induced['r2_a1'].vol.names, rm_TH.induced['r2_a1'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
    {% for name, number in zip(rm_TH.induced['r1_a2'].vol.names, rm_TH.induced['r1_a2'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
    {% for name, number in zip(rm_TH.induced['r2_a2'].vol.names, rm_TH.induced['r2_a2'].vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
  {% endif %}

  {% if dm.magnet.geometry.thermal.with_iron_yoke %}
    {% for name, number in zip(rm_TH.iron_yoke.vol.names, rm_TH.iron_yoke.vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
  {% endif %}

  {% if not dm.magnet.geometry.thermal.use_TSA %}
    {% for name, number in zip(rm_TH.insulator.vol.names, rm_TH.insulator.vol.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
    {% for name, number in zip(rm_TH.insulator.surf.names, rm_TH.insulator.surf.numbers) %}
      <<name>> = Region[ <<number>> ];
    {% endfor %}
  {% endif %}

  {% for cond_name in dm.conductors.keys() %}
    <<nc.omega>><<nc.powered>>_<<cond_name>>_TH = Region[ {
               {% if rm_TH.powered['r1_a1'].conductors[cond_name] %}<<rm_TH.powered['r1_a1'].conductors[cond_name]|join(', ')>>{% endif %}
               {% if rm_TH.powered['r1_a2'].conductors[cond_name] %}, <<rm_TH.powered['r1_a2'].conductors[cond_name]|join(', ')>>{% endif %}
               {% if rm_TH.powered['r2_a1'].conductors[cond_name] %}, <<rm_TH.powered['r2_a1'].conductors[cond_name]|join(', ')>>{% endif %}
               {% if rm_TH.powered['r2_a2'].conductors[cond_name] %}, <<rm_TH.powered['r2_a2'].conductors[cond_name]|join(', ')>>{% endif %}} ];
  {% endfor %}
    <<nc.omega>><<nc.powered>>_TH = Region[ {<<nc.omega>><<nc.powered>>_<<dm.conductors.keys()|join('_TH, ' + nc.omega + nc.powered + '_')>>_TH} ];
  {% if dm.magnet.geometry.thermal.with_iron_yoke %}
    <<nc.omega>><<nc.iron>>_TH = Region[ {<<rm_TH.iron_yoke.vol.names|join(', ')>>} ];
  {% endif %}
  {% if dm.magnet.geometry.thermal.with_wedges %}
    <<nc.omega>><<nc.induced>>_TH = Region[ {
                {% if rm_TH.induced['r1_a1'].vol.names %}<<rm_TH.induced['r1_a1'].vol.names|join(', ')>>{% endif %}
                {% if rm_TH.induced['r1_a2'].vol.names %}, <<rm_TH.induced['r1_a2'].vol.names|join(', ')>>{% endif %}
                {% if rm_TH.induced['r2_a1'].vol.names %}, <<rm_TH.induced['r2_a1'].vol.names|join(', ')>>{% endif %}
                {% if rm_TH.induced['r2_a2'].vol.names %}, <<rm_TH.induced['r2_a2'].vol.names|join(', ')>>{% endif %}} ];
  {% endif %}
  <<nc.omega>><<nc.conducting>>_TH = Region[ {<<nc.omega>><<nc.powered>>_TH{% if dm.magnet.geometry.thermal.with_iron_yoke %}, <<nc.omega>><<nc.iron>>_TH{% endif %}
      {% if dm.magnet.geometry.thermal.with_wedges %}, <<nc.omega>><<nc.induced>>_TH{% endif %}} ];
  {% if not dm.magnet.geometry.thermal.use_TSA %}
    <<nc.omega>><<nc.insulator>>_TH = Region[ {<<rm_TH.insulator.vol.names|join(', ')>>} ];
  {% endif %}
    <<nc.omega>>_TH = Region[ {<<nc.omega>><<nc.powered>>_TH{% if dm.magnet.geometry.thermal.with_iron_yoke %}, <<nc.omega>><<nc.iron>>_TH{% endif %}
      {% if dm.magnet.geometry.thermal.with_wedges %}, <<nc.omega>><<nc.induced>>_TH{% endif %}{% if not dm.magnet.geometry.thermal.use_TSA %}, <<nc.omega>><<nc.insulator>>_TH{% endif %}} ];

  {# the jinja 'do' extension allows to perform actions without variable assignments, practically enabling jinja dicts since '{% dict[new_key] = new_value %}' is not allowed #}
  {% set jcZero_ht = {} %}
  {% for cond_name in dm.conductors.keys() %}
    {% do jcZero_ht.update({cond_name: []}) %}
  {% endfor %}
  {% for turn in dm.magnet.solve.thermal.jc_degradation_to_zero.turns %}
    jcZero_ht<<turn>> = Region[{ht<<turn>>_TH}];
    {% for cond_name in dm.conductors.keys() %}
      {% if 'ht' + str(turn) + '_TH' in rm_TH.powered['r1_a1'].conductors[cond_name] + rm_TH.powered['r1_a2'].conductors[cond_name] + rm_TH.powered['r2_a1'].conductors[cond_name] + rm_TH.powered['r2_a2'].conductors[cond_name] %}
        {% do jcZero_ht.update({cond_name: jcZero_ht[cond_name] + ['ht' + str(turn) + '_TH']}) %}
      {% endif %}
    {% endfor %}
  {% endfor %}
  {% for cond_name in dm.conductors.keys() %}
    jcZero_<<cond_name>> = Region[{<<jcZero_ht[cond_name]|join(', ')>>}];
    jcNonZero_<<cond_name>> = Region[<<nc.omega>><<nc.powered>>_<<cond_name>>_TH];
    jcNonZero_<<cond_name>> -= Region[jcZero_<<cond_name>>];
  {% endfor %}

  {% if dm.magnet.geometry.thermal.use_TSA %}
  //    {% set more_elems = [3348, 3349] %}
  //    {% set bare_layers = bare_layers_1_1 + bare_layers_1_2 + bare_layers_2_1 + bare_layers_2_2 %}
  //    {% set not_more_elems = list(set(rm_TH.thin_shells.mid_turns_layers_poles + bare_layers) - set(more_elems)) %}

  //{% set tags_with_same_tsa_structure = [more_elems, not_more_elems] %}
  //{% set thicknesses_tsa_layers = [[2 * 8.4E-5/4, 2 * 8.4E-5 / 4, 2 * 8.4E-5 / 4, 2 * 8.4E-5 /4], [2 * 8.4E-5/2, 2 * 8.4E-5/2]] %}
  {% set materials_tsa_layers = [[], []] %}

  //{% set n_tsa_layers = [4, 2] %} // sum of all

  {% set bndDir_1 = list(set(rm_TH.boundaries.thermal.temperature.groups['r1_a1']).intersection(bare_layers_2_1)) +
                    list(set(rm_TH.boundaries.thermal.temperature.groups['r2_a1']).intersection(bare_layers_1_1)) +
                    list(set(rm_TH.boundaries.thermal.temperature.groups['r1_a2']).intersection(bare_layers_2_2)) +
                    list(set(rm_TH.boundaries.thermal.temperature.groups['r2_a2']).intersection(bare_layers_1_2)) %}

  {% set bndDir_2 = list(set(rm_TH.boundaries.thermal.temperature.groups['r1_a1']).intersection(bare_layers_1_2)) +
                    list(set(rm_TH.boundaries.thermal.temperature.groups['r2_a1']).intersection(bare_layers_2_2)) +
                    list(set(rm_TH.boundaries.thermal.temperature.groups['r1_a2']).intersection(bare_layers_1_1)) +
                    list(set(rm_TH.boundaries.thermal.temperature.groups['r2_a2']).intersection(bare_layers_2_1)) %}

  {% for nr, tags in enumerate(rm_TH.thin_shells.insulation_types.thin_shells + rm_TH.thin_shells.quench_heaters.thin_shells) %}
    intDomain_1_<<nr + 1>> = Region[{<<set(midLayers_1).intersection(tags)|join(', ')>>}];
    intDomain_2_<<nr + 1>> = Region[{<<set(midLayers_2).intersection(tags)|join(', ')>>}];

    // add Robin boundary conditions
    intDomain_1_<<nr + 1>> += Region[{<<set(bndRobinInt_1_1_1 + bndRobinInt_1_1_2 + bndRobinInt_1_2_1 + bndRobinInt_1_2_2).intersection(tags)|join(', ')>>}];
    intDomain_2_<<nr + 1>> += Region[{<<set(bndRobinInt_2_1_1 + bndRobinInt_2_1_2 + bndRobinInt_2_2_1 + bndRobinInt_2_2_2).intersection(tags)|join(', ')>>}];

    // add Dirichlet boundary conditions
    intDomain_1_<<nr + 1>> += Region[{<<set(bndDir_1).intersection(tags)|join(', ')>>}];
    intDomain_2_<<nr + 1>> += Region[{<<set(bndDir_2).intersection(tags)|join(', ')>>}];

    // add Neumann boundary conditions
    intDomain_1_<<nr + 1>> += Region[{<<set(bndNeuInt_1_1_1 + bndNeuInt_1_1_2 + bndNeuInt_1_2_1 + bndNeuInt_1_2_2).intersection(tags)|join(', ')>>}];
    intDomain_2_<<nr + 1>> += Region[{<<set(bndNeuInt_2_1_1 + bndNeuInt_2_1_2 + bndNeuInt_2_2_1 + bndNeuInt_2_2_2).intersection(tags)|join(', ')>>}];

    // Robin domains 
    bndRobinInt_1_1_1_<<nr + 1>> = Region[{<<set(bndRobinInt_1_1_1).intersection(tags)|join(', ')>>}];
    bndRobinInt_1_1_2_<<nr + 1>> = Region[{<<set(bndRobinInt_1_1_2).intersection(tags)|join(', ')>>}];
    bndRobinInt_1_2_1_<<nr + 1>> = Region[{<<set(bndRobinInt_1_2_1).intersection(tags)|join(', ')>>}];
    bndRobinInt_1_2_2_<<nr + 1>> = Region[{<<set(bndRobinInt_1_2_2).intersection(tags)|join(', ')>>}];
    bndRobinInt_2_1_1_<<nr + 1>> = Region[{<<set(bndRobinInt_2_1_1).intersection(tags)|join(', ')>>}];
    bndRobinInt_2_1_2_<<nr + 1>> = Region[{<<set(bndRobinInt_2_1_2).intersection(tags)|join(', ')>>}];
    bndRobinInt_2_2_1_<<nr + 1>> = Region[{<<set(bndRobinInt_2_2_1).intersection(tags)|join(', ')>>}];
    bndRobinInt_2_2_2_<<nr + 1>> = Region[{<<set(bndRobinInt_2_2_2).intersection(tags)|join(', ')>>}];

    // Neumann domains
    bndNeuInt_1_1_1_<<nr + 1>> = Region[{<<set(bndNeuInt_1_1_1).intersection(tags)|join(', ')>>}];
    bndNeuInt_1_1_2_<<nr + 1>> = Region[{<<set(bndNeuInt_1_1_2).intersection(tags)|join(', ')>>}];
    bndNeuInt_1_2_1_<<nr + 1>> = Region[{<<set(bndNeuInt_1_2_1).intersection(tags)|join(', ')>>}];
    bndNeuInt_1_2_2_<<nr + 1>> = Region[{<<set(bndNeuInt_1_2_2).intersection(tags)|join(', ')>>}];
    bndNeuInt_2_1_1_<<nr + 1>> = Region[{<<set(bndNeuInt_2_1_1).intersection(tags)|join(', ')>>}];
    bndNeuInt_2_1_2_<<nr + 1>> = Region[{<<set(bndNeuInt_2_1_2).intersection(tags)|join(', ')>>}];
    bndNeuInt_2_2_1_<<nr + 1>> = Region[{<<set(bndNeuInt_2_2_1).intersection(tags)|join(', ')>>}];
    bndNeuInt_2_2_2_<<nr + 1>> = Region[{<<set(bndNeuInt_2_2_2).intersection(tags)|join(', ')>>}];
  {% endfor %}

  {% else %} {# not TSA #}

  {% for nr, names in enumerate(rm_TH.boundaries.thermal.temperature.bc.names) %}
    <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.temperature)[nr]>> = Region[ {<<names|join(', ')>>} ];
  {% endfor %}

  {% for nr, names in enumerate(rm_TH.boundaries.thermal.heat_flux.bc.names) %}
    {% if dm.magnet.solve.thermal.He_cooling.sides != 'external' and nr == 0 %}
    general_adiabatic = Region[ {<<names|join(', ')>>} ];
    {% else %}
    <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.heat_flux)[nr - 1 if dm.magnet.solve.thermal.He_cooling.sides != 'external' else nr]>> = Region[ {<<names|join(', ')>>} ];
    {% endif %}
  {% endfor %}

  {% for nr, names in enumerate(rm_TH.boundaries.thermal.cooling.bc.names) %}
    {% if dm.magnet.solve.thermal.He_cooling.enabled and nr == 0 %}
    general_cooling = Region[ {<<names|join(', ')>>} ];
    {% else %}
    <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.cooling)[nr - 1 if dm.magnet.solve.thermal.He_cooling.enabled else nr]>> = Region[ {<<names|join(', ')>>} ];
    {% endif %}
  {% endfor %}

    Bnds_dirichlet = Region[ {<<dm.magnet.solve.thermal.overwrite_boundary_conditions.temperature|join(', ')>>} ];
    Bnds_neumann = Region[ {} ];
    {% if dm.magnet.solve.thermal.He_cooling.sides != 'external' %}
    Bnds_neumann += Region[ general_adiabatic ];
    {% endif %}
    {% if dm.magnet.solve.thermal.overwrite_boundary_conditions.heat_flux %} 
    Bnds_neumann += Region[ {<<dm.magnet.solve.thermal.overwrite_boundary_conditions.heat_flux|join(', ')>>} ];
    {% endif %}

    Bnds_robin = Region[ {} ];
    {% if dm.magnet.solve.thermal.He_cooling.enabled %}
    Bnds_robin += Region[ general_cooling ];
    {% endif %}
    {% if dm.magnet.solve.thermal.overwrite_boundary_conditions.cooling %}
    Bnds_robin += Region[ {<<dm.magnet.solve.thermal.overwrite_boundary_conditions.cooling|join(', ')>>} ];
    {% endif %}

    Bnds_support = Region[ {Bnds_neumann, Bnds_robin} ];

  {% endif %}

  {% if dm.magnet.solve.electromagnetics.solve_type %}
    <<rm_TH.projection_points.name>> = Region[ <<rm_TH.projection_points.number>> ];
  {% endif %}

{% endif %}
}

Function {
{% if dm.magnet.solve.electromagnetics.solve_type %}

      mu0 = 4.e-7 * Pi;
      nu [ Region[{<<rm_EM.air.vol.name>>, <<nc.omega>><<nc.powered>>_EM, <<rm_EM.air_far_field.vol.names[0]>>{% if dm.magnet.geometry.electromagnetics.with_wedges %}, <<nc.omega>><<nc.induced>>_EM{% endif %}}] ]  = 1. / mu0;

    {% if dm.magnet.geometry.electromagnetics.with_iron_yoke %}
      {% for name in rm_EM.iron_yoke.vol.names %}
        nu [ <<name>> ]  = nu<<name>>[$1];
        dnuIronYoke [ <<name>> ]  = dnu<<name>>[$1];
      {% endfor %}
    {% endif %}

    {% for name, current, number in zip(rm_EM.powered['r1_a1'].vol.names + rm_EM.powered['r1_a2'].vol.names + rm_EM.powered['r2_a1'].vol.names + rm_EM.powered['r2_a2'].vol.names,
        rm_EM.powered['r1_a1'].vol.currents + rm_EM.powered['r1_a2'].vol.currents + rm_EM.powered['r2_a1'].vol.currents + rm_EM.powered['r2_a2'].vol.currents,
        rm_EM.powered['r1_a1'].vol.numbers + rm_EM.powered['r1_a2'].vol.numbers + rm_EM.powered['r2_a1'].vol.numbers + rm_EM.powered['r2_a2'].vol.numbers
        ) %}
      js_fct[ <<name>> ] = <<current>>/SurfaceArea[]{ <<number>> };
    {% endfor %}

{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}

  {% for name, number in zip(rm_TH.powered['r1_a1'].vol.names + rm_TH.powered['r1_a2'].vol.names + rm_TH.powered['r2_a1'].vol.names + rm_TH.powered['r2_a2'].vol.names,
  rm_TH.powered['r1_a1'].vol.numbers + rm_TH.powered['r1_a2'].vol.numbers + rm_TH.powered['r2_a1'].vol.numbers + rm_TH.powered['r2_a2'].vol.numbers
  ) %}
  area_fct[ <<name>> ] = SurfaceArea[]{ <<number>> };
  {% endfor %}

  {% if dm.magnet.geometry.thermal.use_TSA %}
    {% for nr, tags in enumerate(rm_TH.boundaries.thermal.temperature.bc.numbers) %}
      bnd_dirichlet_<<nr + 1>>() = {<<tags|join(', ')>>};
      val_temperature_<<nr + 1>> = <<rm_TH.boundaries.thermal.temperature.bc.value[nr]>>;
    {% endfor %}
      num_dirichlet = <<len(rm_TH.boundaries.thermal.temperature.bc.numbers)>>;  // number of different dirichlet boundary cond.

    {% for nr, tags in enumerate(rm_TH.boundaries.thermal.heat_flux.bc.numbers) %}
      bnd_neumann_<<nr + 1>>() = {<<tags|join(', ')>>};
      val_heatFlux_<<nr + 1>> = <<rm_TH.boundaries.thermal.heat_flux.bc.value[nr]>>;
    {% endfor %}
      num_neumann = <<len(rm_TH.boundaries.thermal.heat_flux.bc.numbers)>>;  // number of different neumann boundary cond.

    {% for nr, tags in enumerate(rm_TH.boundaries.thermal.cooling.bc.numbers) %}
      bnd_robin_<<nr + 1>>() = {<<tags|join(', ')>>};
    {% if isinstance(rm_TH.boundaries.thermal.cooling.bc.values[nr][0], str) %}
      val_heatExchCoeff_<<nr + 1>>[] = <<rm_TH.boundaries.thermal.cooling.bc.values[nr][0]>>[$1, $2];
    {% else %}
      val_heatExchCoeff_<<nr + 1>>[] = <<rm_TH.boundaries.thermal.cooling.bc.values[nr][0]>>;
    {% endif %}
      val_Tinf_<<nr + 1>> = <<rm_TH.boundaries.thermal.cooling.bc.values[nr][1]>>;
    {% endfor %}
      num_robin = <<len(rm_TH.boundaries.thermal.cooling.bc.numbers)>>;  // number of different robin boundary cond.
  {% endif %}

      // time steps adaptive time stepping must hit
      Breakpoints = {<<dm.magnet.solve.thermal.time_stepping.breakpoints|join(', ')>>};

  {% if dm.magnet.geometry.thermal.use_TSA %}
        // first idx: 1 layers parallel to radial direction (== normal to phi unit vector)
        //            2 layers parallel to azimuthal direction (== normal to r unit vector)
        // second and third idx: same as bare layers
        // this gives the relation between radius/angle and index 0 to n_ele
    {% for nr, n_ele in enumerate(rm_TH.thin_shells.insulation_types.layers_number + rm_TH.thin_shells.quench_heaters.layers_number) %}
      outerElem_1_1_1_<<nr + 1>> = 0;
      outerElem_2_1_1_<<nr + 1>> = 0;

      outerElem_1_2_1_<<nr + 1>> = <<n_ele>>;
      outerElem_2_2_1_<<nr + 1>> = 0;

      outerElem_1_1_2_<<nr + 1>> = 0;
      outerElem_2_1_2_<<nr + 1>> = <<n_ele>>;

      outerElem_1_2_2_<<nr + 1>> = <<n_ele>>;
      outerElem_2_2_2_<<nr + 1>> = <<n_ele>>;
    {% endfor %}

    {% set no_flip_tags = rm_TH.thin_shells.second_group_is_next['azimuthally'] + rm_TH.thin_shells.second_group_is_next['radially'] %}
    {% set all_dir = bndDir_1 + bndDir_2 %}
    {% set all_neu = bndNeuInt_1_1_1 + bndNeuInt_1_1_2 + bndNeuInt_1_2_1 + bndNeuInt_1_2_2 + bndNeuInt_2_1_1 + bndNeuInt_2_1_2 + bndNeuInt_2_2_1 + bndNeuInt_2_2_2 %}
    {% set all_robin = bndRobinInt_1_1_1 + bndRobinInt_1_1_2 + bndRobinInt_1_2_1 + bndRobinInt_1_2_2 + bndRobinInt_2_1_1 + bndRobinInt_2_1_2 + bndRobinInt_2_2_1 + bndRobinInt_2_2_2 %}

    {% set flip_tags = list(set(rm_TH.thin_shells.mid_turns_layers_poles + all_neu + all_dir + all_robin + ns.all_QH) - set(no_flip_tags))  %}
  {% endif %}

      // --------------- MATERIAL FUNCTIONS ----------------------------------------
    {% set criticalCurrentDensityMacroName = {'Nb-Ti_CUDI1': 'MATERIAL_CriticalCurrentDensity_NiobiumTitanium_CUDI1_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                              'Nb3Sn_Summers': 'MATERIAL_CriticalCurrentDensity_Niobium3Tin_Summers_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                              'Nb3Sn_Bordini': 'MATERIAL_CriticalCurrentDensity_Niobium3Tin_Bordini_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                              'BSCCO2212': 'MATERIAL_CriticalCurrentDensity_BSCCO2212_BSCCO_2212_LBNL_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else '')} %}
    {% set resistivityMacroName = {'Cu': 'MATERIAL_Resistivity_Copper_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                   'Ag': 'MATERIAL_Resistivity_Silver_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                   'SS': 'MATERIAL_Resistivity_SSteel_T'} %}
    {% set thermalConductivityMacroName = {'Cu': 'MATERIAL_ThermalConductivity_Copper_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                           'Ag': 'MATERIAL_ThermalConductivity_Silver_T', 'SS': 'MATERIAL_ThermalConductivity_SSteel_T',
                                           'kapton': 'MATERIAL_ThermalConductivity_Kapton_T', 'G10': 'MATERIAL_ThermalConductivity_G10_T'} %}
    {% set specificHeatCapacityMacroName = {'Cu': 'MATERIAL_SpecificHeatCapacity_Copper_T', 'Ag': 'MATERIAL_SpecificHeatCapacity_Silver_T', 'SS': 'MATERIAL_SpecificHeatCapacity_SSteel_T',
                                            'Nb-Ti': 'MATERIAL_SpecificHeatCapacity_NiobiumTitanium_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                            'Nb3Sn': 'MATERIAL_SpecificHeatCapacity_Niobium3Tin_T' + ('_B' if dm.magnet.solve.electromagnetics.solve_type else ''),
                                            'BSCCO2212': 'MATERIAL_SpecificHeatCapacity_BSCCO2212_T',
                                            'kapton': 'MATERIAL_SpecificHeatCapacity_Kapton_T', 'G10': 'MATERIAL_SpecificHeatCapacity_G10_T', 
                                            'helium': 'MATERIAL_SpecificHeatCapacity_Helium_T'} %}

    {% set thermalConductivityTSAStiffnessMacroName = {'Cu': 'MATERIAL_ThermalConductivity_Copper_TSAStiffness_T', 'SS': 'MATERIAL_ThermalConductivity_SSteel_TSAStiffness_T',
                                            'kapton': 'MATERIAL_ThermalConductivity_Kapton_TSAStiffness_T', 'G10': 'MATERIAL_ThermalConductivity_G10_TSAStiffness_T',
                                            'stycast': 'MATERIAL_ThermalConductivity_Stycast_TSAStiffness_T'} %}

    {% set thermalConductivityTSAMassMacroName = {'Cu': 'MATERIAL_ThermalConductivity_Copper_TSAMass_T', 'SS': 'MATERIAL_ThermalConductivity_SSteel_TSAMass_T',
                                                  'kapton': 'MATERIAL_ThermalConductivity_Kapton_TSAMass_T', 'G10': 'MATERIAL_ThermalConductivity_G10_TSAMass_T',
                                                  'stycast': 'MATERIAL_ThermalConductivity_Stycast_TSAMass_T'} %}

    {% set specificHeatCapacityTSAMacroName = {'Cu': 'MATERIAL_SpecificHeatCapacity_Copper_TSAMass_T', 'SS': 'MATERIAL_SpecificHeatCapacity_SSteel_TSAMass_T',
                                               'kapton': 'MATERIAL_SpecificHeatCapacity_Kapton_TSAMass_T', 'G10': 'MATERIAL_SpecificHeatCapacity_G10_TSAMass_T',
                                               'stycast': 'MATERIAL_SpecificHeatCapacity_Stycast_TSAMass_T'} %}
                                               
    {% for name, cond in dm.conductors.items() %}
      {% if cond.cable.f_inner_voids and cond.cable.f_outer_voids %}
  	    f_inner_voids_<<name>> = <<cond.cable.f_inner_voids>>;
        f_outer_voids_<<name>> = <<cond.cable.f_outer_voids>>;
        f_strand_<<name>> = 1.0 - (<<cond.cable.f_inner_voids>> + <<cond.cable.f_outer_voids>>);
      {% else %}
        {% if cond.strand.type == 'Round' %}
          {% set n_strands = cond.cable.n_strands %}
          {% set A_Strand = cond.cable.n_strands * Pi/4.0 * cond.strand.diameter**2 %}
        {% elif cond.strand.type == 'Rectangular' %}
          {% set n_strands = cond.cable.n_strands if cond.cable.type == 'Rutherford' else 1 %}
          {% set A_Strand = n_strands * cond.strand.bare_width * cond.strand.bare_height %}
        {% endif %}
        {% set A_cable = cond.cable.bare_cable_width * cond.cable.bare_cable_height_mean %}

        {% set f_both_voids = 1.0 - A_Strand / A_cable %}
        {% set f_inner_voids = f_both_voids * (0.5 - 1.0/n_strands) %}
        {% set f_outer_voids = f_both_voids * (0.5 + 1.0/n_strands) %}

        f_inner_voids_<<name>> = <<f_inner_voids>>;
        f_outer_voids_<<name>> = <<f_outer_voids>>;
        f_strand_<<name>> = 1.0 - <<f_both_voids>>;
      {% endif %}

      f_stabilizer_<<name>> = f_strand_<<name>> * <<cond.strand.Cu_noCu_in_strand>> / (1. + <<cond.strand.Cu_noCu_in_strand>>);
      f_sc_<<name>> = f_strand_<<name>> * (1.0 - <<cond.strand.Cu_noCu_in_strand>> / (1. + <<cond.strand.Cu_noCu_in_strand>>));
    {% endfor %}

      source_current = <<dm.power_supply.I_initial>>;

    {# the namespace object with attribute 'conductor' is necessary to store a Pydantic class object like 'cond' #}
    {% set current_cond = namespace(conductor={}) %}
    {% for name, cond in dm.conductors.items() %}
      <<criticalCurrentDensity("jcNonZero_" + name, cond, time_trigger=1e6, cond_name=name)>>
    {% endfor %}
    {% for turn, t_trigger in zip(dm.magnet.solve.thermal.jc_degradation_to_zero.turns, dm.magnet.solve.thermal.jc_degradation_to_zero.t_trigger) %}
      {% for name, cond in dm.conductors.items() %}
        {% if 'ht' + str(turn) + '_TH' in jcZero_ht[name] %}
          {% set current_cond.conductor = cond %}
          {% set current_cond.name = name %}

        {% endif %}
      {% endfor %}
      <<criticalCurrentDensity("jcZero_ht" + str(turn), cond=current_cond.conductor, time_trigger=t_trigger, cond_name=current_cond.name)>>
    {% endfor %}

    {% for name, cond in dm.conductors.items() %}
      rho[<<nc.omega>><<nc.powered>>_<<name>>_TH] = EffectiveResistivity[<<materials[resistivityMacroName[cond.strand.material_stabilizer]](RRR=cond.strand.RRR)>>]{f_stabilizer_<<name>>};
    {% endfor %}

      // effective thermal conductivity of the bare part
    {% for name, cond in dm.conductors.items() %}
      kappa[<<nc.omega>><<nc.powered>>_<<name>>_TH] = RuleOfMixtures[
        <<materials[thermalConductivityMacroName[cond.strand.material_stabilizer]
      ](RRR=cond.strand.RRR)>>
      {% if cond.cable.material_inner_voids != 'helium' %}
      , <<materials[thermalConductivityMacroName[cond.cable.material_inner_voids]]()>>
      {% endif %}
      {% if cond.cable.material_outer_voids != 'helium' %}
      , <<materials[thermalConductivityMacroName[cond.cable.material_outer_voids]]()>>
      {% endif %}
    ]
    {f_stabilizer_<<name>>
      {% if cond.cable.material_inner_voids != 'helium' %}
      , f_inner_voids_<<name>>
      {% endif %}
      {% if cond.cable.material_outer_voids != 'helium' %}
      ,  f_outer_voids_<<name>>
      {% endif %}
    };
    {% endfor %}

      // heat capacity of bare part
    {% for name, cond in dm.conductors.items() %}
    {% if cond.strand.material_superconductor == 'Nb-Ti' %}
      heatCap[<<nc.omega>><<nc.powered>>_<<name>>_TH] = RuleOfMixtures[
        <<materials[specificHeatCapacityMacroName[cond.strand.material_stabilizer]]()>>,
        <<materials[specificHeatCapacityMacroName[cond.strand.material_superconductor]](C1=cond.Jc_fit.C1_CUDI1, C2=cond.Jc_fit.C2_CUDI1, current=dm.power_supply.I_initial)>>, 
        <<materials[specificHeatCapacityMacroName[cond.cable.material_inner_voids]]()>>,
        <<materials[specificHeatCapacityMacroName[cond.cable.material_outer_voids]]()>>
      ]
      {
        f_stabilizer_<<name>>,
        f_sc_<<name>>,
        f_inner_voids_<<name>>,
        f_outer_voids_<<name>>
      };
    {% else %}
      heatCap[<<nc.omega>><<nc.powered>>_<<name>>_TH] = RuleOfMixtures[
        <<materials[specificHeatCapacityMacroName[cond.strand.material_stabilizer]]()>>,
        <<materials[specificHeatCapacityMacroName[cond.strand.material_superconductor]]()>>,
        <<materials[specificHeatCapacityMacroName[cond.cable.material_inner_voids]]()>>,
        <<materials[specificHeatCapacityMacroName[cond.cable.material_outer_voids]]()>>
      ]
      {
        f_stabilizer_<<name>>, 
        f_sc_<<name>>,
        f_inner_voids_<<name>>, 
        f_outer_voids_<<name>>
      };
    {% endif %}
    {% endfor %}

      // joule losses of bare part
    {% if dm.magnet.solve.electromagnetics.solve_type %}
      jouleLosses[] = CFUN_quenchState_Ic[criticalCurrentDensity[$1, $2] * area_fct[]]{source_current} * rho[$1, $2] * SquNorm[source_current/area_fct[]];
    {% else %}
      jouleLosses[] = CFUN_quenchState_Ic[criticalCurrentDensity[$1] * area_fct[]]{source_current} * rho[$1] * SquNorm[source_current/area_fct[]];
    {% endif %}

    {% if dm.magnet.geometry.thermal.with_wedges %}
      // thermal conductivity of the wedges
      kappa[<<nc.omega>><<nc.induced>>_TH] = <<materials[thermalConductivityMacroName[dm.magnet.solve.wedges.material]](RRR=dm.magnet.solve.wedges.RRR)>>;

      // heat capacity of wedges
      heatCap[<<nc.omega>><<nc.induced>>_TH] = <<materials[specificHeatCapacityMacroName[dm.magnet.solve.wedges.material]]()>>;
    {% endif %}

    {% if dm.magnet.geometry.thermal.with_iron_yoke %}
      // thermal conductivity of the iron yoke
      kappa[<<nc.omega>><<nc.iron>>_TH] = 300;

      // heat capacity of iron yoke
      heatCap[ <<nc.omega>><<nc.iron>>_TH ] = 50;
    {% endif %}

  {% if dm.magnet.geometry.thermal.use_TSA %}
      For i In {1:num_dirichlet}
        // piece-wise defined const_temp
        const_temp[Region[bnd_dirichlet~{i}]] = val_temperature~{i};
      EndFor

      For n In {1:num_neumann}
        // piece-wise defined heatFlux
        heatFlux[Region[bnd_neumann~{n}]] = val_heatFlux~{n};
      EndFor

      For r In {1:num_robin}
        // piece-wise defined heatExchCoeff
        heatExchCoeff[Region[bnd_robin~{r}]] = val_heatExchCoeff~{r}[$1, $2];
        Tinf[Region[bnd_robin~{r}]] = val_Tinf~{r};
      EndFor
  {% else %}
      // thermal conductivity of the insulation
      kappa[<<nc.omega>><<nc.insulator>>_TH] = <<materials[thermalConductivityMacroName[list(dm.conductors.values())[0].cable.material_insulation]]()>>;

      // heat capacity of insulation
      heatCap[ <<nc.omega>><<nc.insulator>>_TH ] = <<materials[specificHeatCapacityMacroName[list(dm.conductors.values())[0].cable.material_insulation]]()>>;
  {% endif %}

  {% if dm.magnet.geometry.thermal.use_TSA %}
      // --------------- Thickness function ----------------------------------------
      // check if we need to flip the order of the layers
      // TODO: this is not very elegant, but it works
      // TODO: check if delta[i] instead of delta~{i} works
      {% set TSAinsulationAndQH_layers_number = rm_TH.thin_shells.insulation_types.layers_number + rm_TH.thin_shells.quench_heaters.layers_number %}
      {% set TSAinsulationAndQH_thicknesses = rm_TH.thin_shells.insulation_types.thicknesses + rm_TH.thin_shells.quench_heaters.thicknesses %}
      {% set TSAinsulationAndQH_thin_shells = rm_TH.thin_shells.insulation_types.thin_shells + rm_TH.thin_shells.quench_heaters.thin_shells %}
      {% set TSAinsulationAndQH_material = rm_TH.thin_shells.insulation_types.layers_material + rm_TH.thin_shells.quench_heaters.layers_material %}

      {% for nr, n_ele in enumerate(TSAinsulationAndQH_layers_number) %}
        {% for nr_thickness, thickness in enumerate(TSAinsulationAndQH_thicknesses[nr]) %}
          {% for tag in TSAinsulationAndQH_thin_shells[nr] %}
            {% if tag in flip_tags %}
              delta_<<n_ele - nr_thickness - 1>>[Region[<<tag>>]] = <<thickness>>;
              {% for k in range(1,3) %}
                {% for l in range(1,3) %}
                  thermalConductivityMass_<<k>>_<<l>>_<<n_ele - nr_thickness - 1>>[Region[<<tag>>]] = <<TSA_materials[thermalConductivityTSAMassMacroName[TSAinsulationAndQH_material[nr][nr_thickness]]](T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, l=l, GaussianPoints=2)>>;

                  thermalConductivityStiffness_<<k>>_<<l>>_<<n_ele - nr_thickness - 1>>[Region[<<tag>>]] = <<TSA_materials[thermalConductivityTSAStiffnessMacroName[TSAinsulationAndQH_material[nr][nr_thickness]]](T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, l=l, GaussianPoints=2)>>;

                  specificHeatCapacity_<<k>>_<<l>>_<<n_ele - nr_thickness - 1>>[Region[<<tag>>]] = <<TSA_materials[specificHeatCapacityTSAMacroName[TSAinsulationAndQH_material[nr][nr_thickness]]](T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, l=l, GaussianPoints=2)>>;
                {% endfor %}
              {% endfor %}
            {% else %}
              delta_<<nr_thickness>>[Region[<<tag>>]] = <<thickness>>;
              {% for k in range(1,3) %}
                {% for l in range(1,3) %}
            thermalConductivityMass_<<k>>_<<l>>_<<nr_thickness>>[Region[<<tag>>]] = <<TSA_materials[thermalConductivityTSAMassMacroName[TSAinsulationAndQH_material[nr][nr_thickness]]](T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, l=l, GaussianPoints=2)>>;

            thermalConductivityStiffness_<<k>>_<<l>>_<<nr_thickness>>[Region[<<tag>>]] = <<TSA_materials[thermalConductivityTSAStiffnessMacroName[TSAinsulationAndQH_material[nr][nr_thickness]]](T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, l=l, GaussianPoints=2)>>;

            specificHeatCapacity_<<k>>_<<l>>_<<nr_thickness>>[Region[<<tag>>]] = <<TSA_materials[specificHeatCapacityTSAMacroName[TSAinsulationAndQH_material[nr][nr_thickness]]](T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, l=l, GaussianPoints=2)>>;
              {% endfor %}
            {% endfor %}
            {% endif %}
          {% endfor %}
        {% endfor %}
      {% endfor %}

    {% for nr, n_ele in enumerate(rm_TH.thin_shells.quench_heaters.layers_number) %}
      {% for nr_thickness, thickness in enumerate(rm_TH.thin_shells.quench_heaters.thicknesses[nr]) %}
        {% for tag in rm_TH.thin_shells.quench_heaters.thin_shells[nr] %}
          {% set qh_indexPlusOne = rm_TH.thin_shells.quench_heaters.label[nr][nr_thickness] %}
          {% if qh_indexPlusOne %}
          {% set qh_dict = dm.quench_protection.quench_heaters %}
          {% set qh_index = int(qh_indexPlusOne or 1E20) - 1 %}
          {% set l_SS = qh_dict.l_stainless_steel[qh_index] / (qh_dict.l_copper[qh_index] + qh_dict.l_stainless_steel[qh_index]) * qh_dict.l[qh_index] %}
          {% endif %}

          {% if tag in flip_tags %}
            {% for k in range(1,3) %}
              {% if qh_indexPlusOne %}
                powerDensity_<<k>>_<<n_ele - nr_thickness - 1>>[Region[<<tag>>]] = <<TSA_materials['MATERIAL_QuenchHeater_SSteel_t_T'](t_on=qh_dict.t_trigger[qh_index], U_0=qh_dict.U0[qh_index], C=qh_dict.C[qh_index], R_warm=qh_dict.R_warm[qh_index], w_SS=qh_dict.w[qh_index], h_SS=qh_dict.h[qh_index], l_SS=l_SS, mode=1, time="$Time", T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, GaussianPoints=2)>>;
              {% else %}
                powerDensity_<<k>>_<<n_ele - nr_thickness - 1>>[Region[<<tag>>]] = 0;
              {% endif %}
            {% endfor %}
          {% else %}
            {% for k in range(1,3) %}
              {% if qh_indexPlusOne %}
                powerDensity_<<k>>_<<nr_thickness>>[Region[<<tag>>]] = <<TSA_materials['MATERIAL_QuenchHeater_SSteel_t_T'](t_on=qh_dict.t_trigger[qh_index], U_0=qh_dict.U0[qh_index], C=qh_dict.C[qh_index], R_warm=qh_dict.R_warm[qh_index], w_SS=qh_dict.w[qh_index], h_SS=qh_dict.h[qh_index], l_SS=l_SS, mode=1, time="$Time",T_i="$1", T_iPlusOne="$2", thickness_TSA="$3", k=k, GaussianPoints=2)>>;
              {% else %}
                powerDensity_<<k>>_<<nr_thickness>>[Region[<<tag>>]] = 0;
              {% endif %}
            {% endfor %}
          {% endif %}
        {% endfor %}
      {% endfor %}
    {% endfor %}

  {% endif %}

{% endif %}
}

{% if dm.magnet.solve.thermal.solve_type %}

  {% if dm.magnet.geometry.thermal.use_TSA %}
    {% set lines_tags =  rm_TH.boundaries.thermal.temperature.groups['r1_a1'] +
    rm_TH.boundaries.thermal.temperature.groups['r1_a2'] +
    rm_TH.boundaries.thermal.temperature.groups['r2_a1'] +
    rm_TH.boundaries.thermal.temperature.groups['r2_a2'] +
    rm_TH.boundaries.thermal.cooling.groups['r1_a1'] +
    rm_TH.boundaries.thermal.cooling.groups['r1_a2'] +
    rm_TH.boundaries.thermal.cooling.groups['r2_a1'] +
    rm_TH.boundaries.thermal.cooling.groups['r2_a2'] +
    rm_TH.thin_shells.mid_turns_layers_poles %}

    // split to avoid error for two touching lines in different intDomains
    {% set lines_tags_1 = set(lines_tags).intersection(midLayers_1 + bndDir_1 + bndNeuInt_1_1_1 + bndNeuInt_1_2_1 + bndNeuInt_1_1_2 + bndNeuInt_1_2_2 + bndRobinInt_1_1_1 + bndRobinInt_1_2_1 + bndRobinInt_1_1_2 + bndRobinInt_1_2_2) %}
    {% set lines_tags_2 = set(lines_tags).intersection(midLayers_2 + bndDir_2 + bndNeuInt_2_1_1 + bndNeuInt_2_2_1 + bndNeuInt_2_1_2 + bndNeuInt_2_2_2 + bndRobinInt_2_1_1 + bndRobinInt_2_2_1 + bndRobinInt_2_1_2 + bndRobinInt_2_2_2) %}

    Constraint {
      coordList_Python_1_1() = {<<rc.neighbouring_nodes.groups['1_1']|join(', ')>>};
      coordList_Python_2_1() = {<<rc.neighbouring_nodes.groups['2_1']|join(', ')>>};
      coordList_Python_1_2() = {<<rc.neighbouring_nodes.groups['1_2']|join(', ')>>};
      coordList_Python_2_2() = {<<rc.neighbouring_nodes.groups['2_2']|join(', ')>>};
      For i In {1:2}
        For j In {1:2}
          { Name Temperature~{i}~{j} ;
            Case {
                // Link DoF of auxiliary shells to actual temperature
              { Region midLayers~{i}~{j} ; Type Link;
                RegionRef Bare_Layers~{i}~{j} ; Coefficient 1;
                // coordList or coordList_Python
                Function shiftCoordinate[X[], Y[], Z[]]{coordList_Python~{i}~{j}()};
              }
              If (num_dirichlet > 0)
                // TODO: proper time dependent boundary conditions
                { Region Region[bndDir~{i}~{j}]; Type Assign;
                  Value const_temp[]; }
              EndIf
            }
          }
        EndFor
      EndFor

      {% if dm.magnet.mesh.thermal.isothermal_conductors or dm.magnet.mesh.thermal.isothermal_wedges %}
        { Name isothermal_surs~{1}~{1} ;
          Case {
          {% if dm.magnet.mesh.thermal.isothermal_conductors %}
            {% for tag in rm_TH.powered['r1_a1'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.conductors['1_1'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          {% if dm.magnet.mesh.thermal.isothermal_wedges %}
            {% for tag in rm_TH.induced['r1_a1'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.wedges['1_1'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          }
        }
        { Name isothermal_surs~{2}~{1} ;
          Case {
          {% if dm.magnet.mesh.thermal.isothermal_conductors %}
            {% for tag in rm_TH.powered['r2_a1'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.conductors['2_1'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          {% if dm.magnet.mesh.thermal.isothermal_wedges %}
            {% for tag in rm_TH.induced['r2_a1'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.wedges['2_1'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          }
        }
        { Name isothermal_surs~{1}~{2} ;
          Case {
          {% if dm.magnet.mesh.thermal.isothermal_conductors %}
            {% for tag in rm_TH.powered['r1_a2'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.conductors['1_2'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          {% if dm.magnet.mesh.thermal.isothermal_wedges %}
            {% for tag in rm_TH.induced['r1_a2'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.wedges['1_2'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          }
        }
        { Name isothermal_surs~{2}~{2} ;
          Case {
          {% if dm.magnet.mesh.thermal.isothermal_conductors %}
            {% for tag in rm_TH.powered['r2_a2'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.conductors['2_2'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          {% if dm.magnet.mesh.thermal.isothermal_wedges %}
            {% for tag in rm_TH.induced['r2_a2'].vol.numbers %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.wedges['2_2'][tag]|join(', ')>>];
                }
            {% endfor %}
          {% endif %}
          }
        }

        {% if dm.magnet.mesh.thermal.isothermal_conductors %}
        { Name isothermal_lines_1 ;
          Case {
            {% for tag in lines_tags_1 %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.thin_shells[tag]|join(', ')>>];
                }
            {% endfor %}
          }
        }
        { Name isothermal_lines_2 ;
          Case {
            {% for tag in lines_tags_2 %}
              { Region Region[<<tag>>] ; Type Link;
                RegionRef Region[<<tag>>] ; Coefficient 1;
                Function Vector[<<rc.isothermal_nodes.thin_shells[tag]|join(', ')>>];
                }
            {% endfor %}
          }
        }
        {% endif %}
      {% endif %}
    }
  {% endif %}

{% endif %}

Constraint {
{% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name Dirichlet_a_Mag;
    Case {
      { Region <<nc.boundary>><<nc.omega>> ; Value 0.; }
    }
  }
  { Name SourceCurrentDensityZ;
    Case {
      { Region <<nc.omega>><<nc.powered>>_EM ; Value js_fct[]; }
    }
  }
{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}
  { Name initTemp ;
    Case {
      {% if not dm.magnet.geometry.thermal.use_TSA %}
        {% for nr, names in enumerate(rm_TH.boundaries.thermal.temperature.bc.names) %}
        { Region <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.temperature)[nr]>>; Value <<rm_TH.boundaries.thermal.temperature.bc.value[nr]>>;  Type Assign;  } // boundary condition
        {% endfor %}
      {% endif %}
      {% if dm.magnet.solve.thermal.solve_type == 'transient' %}
        {% if dm.magnet.geometry.thermal.use_TSA %}{ Region Region[{allLayers, midLayers}] ; Value <<dm.magnet.solve.thermal.init_temperature>> ; Type Init; }{% endif %}
        { Region <<nc.omega>>_TH ; Value <<dm.magnet.solve.thermal.init_temperature>> ; Type Init; } // init. condition
      {% endif %}
    }
  }
  {% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name Dirichlet_a_projection;
    Case {
      { Region <<rm_TH.projection_points.name>> ; Value 0; Type Assign; }
    }
  }
  {% endif %}
{% endif %}
}

FunctionSpace {
{% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name Hcurl_a_Mag_2D; Type Form1P; // Magnetic vector potential a
    BasisFunction {
      { Name se; NameOfCoef ae; Function BF_PerpendicularEdge;
        Support <<nc.omega>>_EM ; Entity NodesOf[ All ]; }
    }
    Constraint {
      { NameOfCoef ae; EntityType NodesOf;
        NameOfConstraint Dirichlet_a_Mag; }
    }
  }

  { Name Hregion_j_Mag_2D; Type Vector; // Electric current density js
    BasisFunction {
      { Name sr; NameOfCoef jsr; Function BF_RegionZ;
        Support <<nc.omega>><<nc.powered>>_EM; Entity <<nc.omega>><<nc.powered>>_EM; }
    }
    Constraint {
      { NameOfCoef jsr; EntityType Region;
        NameOfConstraint SourceCurrentDensityZ; }
    }
  }

  {% if dm.magnet.solve.thermal.solve_type %}
  { Name H_curl_a_artificial_dof; Type Form1P;  
    BasisFunction {
      { Name se_after_projection; NameOfCoef ae_after_projection; Function BF_PerpendicularEdge;
        Support <<nc.omega>>_TH ; Entity NodesOf[ All ]; }
    }
    // not needed since boundary is not part of <<nc.omega>>_TH
    Constraint {
      { NameOfCoef ae_after_projection; EntityType NodesOf;
        NameOfConstraint Dirichlet_a_projection; }     
    }
  }                                               
  {% endif %}
{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}
  { Name Hgrad_T; Type Form0;
    BasisFunction {
      { Name un;  NameOfCoef ui;  Function BF_Node;
        {% if dm.magnet.geometry.thermal.use_TSA %}
          Support Region[ <<nc.omega>>_TH ]; Entity NodesOf[All, Not allLayers];
        {% else %}
          Support Region[{<<nc.omega>>_TH, Bnds_support}] ; Entity NodesOf[All];
        {% endif %}
      }

    {% if dm.magnet.geometry.thermal.use_TSA %}
      // temperature on shells following checkered support idea as indicated
      // by two indices
      // FYI: another possibility would be to treat the extremity points of
      // the shells separately
      For i In {1:2}
        For j In {1:2}
          { Name udn~{i}~{j}; NameOfCoef udi~{i}~{j}; Function BF_Node;
            Support Region[{midLayers~{i}~{j}, Domain_Insulated_Str~{i}~{j}}];
            Entity NodesOf[{midLayers~{i}~{j}, Bare_Layers~{i}~{j}}]; }
        EndFor
      EndFor
    {% endif %}
    }

  {% if dm.magnet.geometry.thermal.use_TSA %}
    SubSpace {
      // "vertical" subspaces, up and down are connected via thin shell
      // vertical thin shells
      { Name Shell_Up_1;   NameOfBasisFunction {udn_1_1, udn_1_2};}
      { Name Shell_Down_1; NameOfBasisFunction {udn_2_2, udn_2_1};}

      // "horizontal" subspaces, up and down are connected via thin shell
      { Name Shell_Up_2;   NameOfBasisFunction {udn_1_1, udn_2_1}; }
      { Name Shell_Down_2; NameOfBasisFunction {udn_2_2, udn_1_2}; }
    }
  {% endif %}

    Constraint {
    {% if dm.magnet.geometry.thermal.use_TSA %}
      For i In {1:2}
        For j In {1:2}
          { NameOfCoef udi~{i}~{j};  EntityType NodesOf;
            NameOfConstraint Temperature~{i}~{j}; }
          {% if dm.magnet.mesh.thermal.isothermal_conductors %}
            {NameOfCoef udi~{i}~{j};  EntityType NodesOf;
            NameOfConstraint isothermal_surs~{i}~{j}; }
          {% endif %}
          { NameOfCoef udi~{i}~{j};  EntityType NodesOf;
            NameOfConstraint initTemp; }
        EndFor
      EndFor
    {% endif %}
      { NameOfCoef ui; EntityType NodesOf; NameOfConstraint initTemp; }
      // do not constraint second order basis function as it's already covered by ui
    }
  }

  {% if dm.magnet.geometry.thermal.use_TSA %}
    {% for nr, n_ele in enumerate(TSAinsulationAndQH_layers_number) %}
      For i In {1:<<n_ele>>-1}
        For j In {1:2}
          { Name Hgrad_T~{i}~{j}~{<<nr + 1>>}; Type Form0 ;
            BasisFunction {
              { Name sn~{i}~{j}~{<<nr + 1>>}; NameOfCoef Tn~{i}~{j}~{<<nr + 1>>} ; Function BF_Node ;
                Support intDomain~{j}~{<<nr + 1>>} ; Entity NodesOf[ All ] ; }
            }
            Constraint {
            {% if dm.magnet.mesh.thermal.isothermal_conductors %}
              { NameOfCoef Tn~{i}~{j}~{<<nr + 1>>};  EntityType NodesOf;
                NameOfConstraint isothermal_lines~{j}; }
            {% endif %}
              { NameOfCoef Tn~{i}~{j}~{<<nr + 1>>};  EntityType NodesOf;
                NameOfConstraint initTemp; }
            }
          }
        EndFor
      EndFor
    {% endfor %}
  {% endif %}
{% endif %}
}

Jacobian {
{% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name Jac_Vol_EM ;
    Case {
      { Region <<nc.omega>><<nc.air_far_field>>_EM ;
        Jacobian VolSphShell {<<rm_EM.air_far_field.vol.radius_in>>, <<rm_EM.air_far_field.vol.radius_out>>} ; }
      { Region All ; Jacobian Vol ; }
    }
  }
{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}
  { Name Jac_Vol_TH ;
    Case {
      { Region All ; Jacobian Vol ; }
    }
  }
  { Name Jac_Sur_TH ;
    Case {
      { Region All ; Jacobian Sur ; }
    }
  }
{% endif %}
}

Integration {
{% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name Int_EM ;
    Case {
      { Type Gauss ;
        Case {
          { GeoElement Point ; NumberOfPoints 1 ; }
          { GeoElement Line ; NumberOfPoints 2 ; }
          { GeoElement Triangle ; NumberOfPoints 3 ; }
          { GeoElement Quadrangle ; NumberOfPoints 4 ; }
        }
      }
    }
  }
{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}
  { Name Int_line_TH ;
    Case {
      { Type Gauss ;
        Case {
          { GeoElement Line ; NumberOfPoints 2 ; }
        }
      }
    }
  }

  { Name Int_conducting_TH ;
    Case {
      { Type Gauss ;
        Case {
          { GeoElement Triangle ; NumberOfPoints 3 ; }
          { GeoElement Quadrangle ; NumberOfPoints 4 ; }
        }
      }
    }
  }

  { Name Int_insulating_TH ;
    Case {
      { Type Gauss ;
        Case {
          { GeoElement Triangle ; NumberOfPoints 3 ; }
          { GeoElement Quadrangle ; NumberOfPoints 4 ; }
        }
      }
    }
  }
{% endif %}
}

Formulation {
{% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name Magnetostatics_a_2D; Type FemEquation;
    Quantity {
      { Name a ; Type Local; NameOfSpace Hcurl_a_Mag_2D; }
      { Name js; Type Local; NameOfSpace Hregion_j_Mag_2D; }
    }
    Equation {
      Integral { [ nu[{d a}] * Dof{d a} , {d a} ];
        In <<nc.omega>>_EM; Jacobian Jac_Vol_EM; Integration Int_EM; }

    {% if dm.magnet.geometry.electromagnetics.with_iron_yoke %}
      Integral { JacNL[ dnuIronYoke[{d a}] * Dof{d a} , {d a} ];
        In <<nc.omega>><<nc.iron>>_EM; Jacobian Jac_Vol_EM; Integration Int_EM; }
    {% endif %}

      Integral { [ -Dof{js} , {a} ];
        In <<nc.omega>><<nc.powered>>_EM; Jacobian Jac_Vol_EM; Integration Int_EM; }
    }
  }

  {% if dm.magnet.solve.thermal.solve_type %}
  // Dummy formulation just to save the values of the norm of B from the EM mesh on the Gaussian points of
  // the thermal mesh. Alternatively, a Galerkin projection could be used.
  { Name Projection_EM_to_TH; Type FemEquation;
    Quantity {
      {Name a_before_projection; Type Local; NameOfSpace Hcurl_a_Mag_2D; }
      {Name a_artificial_dof; Type Local; NameOfSpace H_curl_a_artificial_dof; }
    }
    Equation {
      Integral { [ - SetVariable[Norm[{d a_before_projection}], ElementNum[], QuadraturePointIndex[]]{$Bnorm}, {d a_artificial_dof} ];
        In <<nc.omega>><<nc.powered>>_TH; Integration Int_conducting_TH; Jacobian Jac_Vol_TH; }

        Integral { [ Dof{d a_artificial_dof}, {d a_artificial_dof} ];
        In <<nc.omega>><<nc.powered>>_TH; Integration Int_conducting_TH; Jacobian Jac_Vol_TH; }
    }
  }                                              
  {% endif %}
{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}
  { Name Thermal_T;   Type FemEquation;
    Quantity {
      // cont temperature
      { Name T; Type Local; NameOfSpace Hgrad_T; }
      {% if dm.magnet.geometry.thermal.use_TSA %}
        For j In {1:2} // "vertical" and "horizontal" separated
          {% for nr, n_ele in enumerate(TSAinsulationAndQH_layers_number) %}

            // outer temp up
            { Name Ti~{0}~{j}~{<<nr + 1>>}; Type Local;
                NameOfSpace Hgrad_T[Shell_Up~{j}]; }
            // auxiliary shells in between
              For i In {1:<<n_ele>>-1}
                  { Name Ti~{i}~{j}~{<<nr + 1>>} ; Type Local ;
                    NameOfSpace Hgrad_T~{i}~{j}~{<<nr + 1>>}; }
              EndFor
            //outer temp down
            { Name Ti~{<<n_ele>>}~{j}~{<<nr + 1>>}; Type Local;
              NameOfSpace Hgrad_T[Shell_Down~{j}]; }
          {% endfor %}
        EndFor
      {% endif %}
    }

    Equation {
      {% if dm.magnet.solve.electromagnetics.solve_type %}
      Integral { [ kappa[{T}, GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] * Dof{d T} , {d T} ] ;
        In Region[ {<<nc.omega>><<nc.powered>>_TH{% if dm.magnet.geometry.thermal.with_iron_yoke %}, <<nc.omega>><<nc.iron>>{% endif %}{% if dm.magnet.geometry.thermal.with_wedges %}, <<nc.omega>><<nc.induced>>_TH{% endif %} } ]; Integration Int_conducting_TH ; Jacobian Jac_Vol_TH ; }
      {% else %}
      Integral { [ kappa[{T}] * Dof{d T} , {d T} ] ;
        In Region[ {<<nc.omega>><<nc.powered>>_TH{% if dm.magnet.geometry.thermal.with_iron_yoke %}, <<nc.omega>><<nc.iron>>{% endif %}{% if dm.magnet.geometry.thermal.with_wedges %}, <<nc.omega>><<nc.induced>>_TH{% endif %} } ]; Integration Int_conducting_TH ; Jacobian Jac_Vol_TH ; }
      {% endif %}

      {% if dm.magnet.solve.electromagnetics.solve_type %}
      Integral { DtDof[ heatCap[{T}, GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] * Dof{T}, {T} ];
        In Region[ {<<nc.omega>><<nc.powered>>_TH{% if dm.magnet.geometry.thermal.with_iron_yoke %}, <<nc.omega>><<nc.iron>>{% endif %}{% if dm.magnet.geometry.thermal.with_wedges %}, <<nc.omega>><<nc.induced>>_TH{% endif %} } ]; Integration Int_conducting_TH; Jacobian Jac_Vol_TH;  }
      {% else %}
      Integral { DtDof[ heatCap[{T}] * Dof{T}, {T} ];
        In Region[ {<<nc.omega>><<nc.powered>>_TH{% if dm.magnet.geometry.thermal.with_iron_yoke %}, <<nc.omega>><<nc.iron>>{% endif %}{% if dm.magnet.geometry.thermal.with_wedges %}, <<nc.omega>><<nc.induced>>_TH{% endif %} } ]; Integration Int_conducting_TH; Jacobian Jac_Vol_TH;  }
      {% endif %}

      {% if not dm.magnet.geometry.thermal.use_TSA %}
        {% if dm.magnet.solve.electromagnetics.solve_type %}
      Integral { [ kappa[{T}, GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] * Dof{d T} , {d T} ] ;
        In <<nc.omega>><<nc.insulator>>_TH; Integration Int_insulating_TH ; Jacobian Jac_Vol_TH ; }
        {% else %}
      Integral { [ kappa[{T}] * Dof{d T} , {d T} ] ;
        In <<nc.omega>><<nc.insulator>>_TH; Integration Int_insulating_TH ; Jacobian Jac_Vol_TH ; }
        {% endif %}

        {% if dm.magnet.solve.electromagnetics.solve_type %}
      Integral { DtDof[ heatCap[{T}, GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] * Dof{T}, {T} ];
        In <<nc.omega>><<nc.insulator>>_TH; Integration Int_insulating_TH; Jacobian Jac_Vol_TH;  }
        {% else %}
      Integral { DtDof[ heatCap[{T}] * Dof{T}, {T} ];
        In <<nc.omega>><<nc.insulator>>_TH; Integration Int_insulating_TH; Jacobian Jac_Vol_TH;  }
        {% endif %}
      {% endif %}

    // TODO: implement derivatives, missing copper for example
    /*   Integral { JacNL[ dkappadT[{T}, {d a}] * {d T} * Dof{T} , {d T} ] ;
         In <<nc.omega>>_TH; Integration Int<> ; Jacobian Jac_Vol_TH ; } */

    {% if dm.magnet.solve.electromagnetics.solve_type %}
      Integral { [ - jouleLosses[{T}, GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}], {T}];
        In <<nc.omega>><<nc.powered>>_TH; Integration Int_conducting_TH; Jacobian Jac_Vol_TH;  }
    {% else %}
      Integral { [ - jouleLosses[{T}], {T}];
        In <<nc.omega>><<nc.powered>>_TH; Integration Int_conducting_TH; Jacobian Jac_Vol_TH;  }
    {% endif %}

      {% if dm.magnet.geometry.thermal.use_TSA %}
        {% for nr, n_ele in enumerate(TSAinsulationAndQH_layers_number) %}
          For i In {0:<<n_ele-1>>} // loop over 1D FE elements
            For j In {1:2} // separation between vertical and horizontal
              {% for k in range(1,3) %}
                {% for l in range(1,3) %}
                Integral {
                  [  thermalConductivityMass_<<k>>_<<l>>~{i}[{Ti~{i}~{j}~{<<nr + 1>>}}, {Ti~{i+1}~{j}~{<<nr + 1>>}}, delta~{i}[]] *
                    Dof{d Ti~{i + <<k>> - 1}~{j}~{<<nr + 1>>}} , {d Ti~{i + <<l>> - 1}~{j}~{<<nr + 1>>}}];
                    In intDomain~{j}~{<<nr + 1>>}; Integration Int_line_TH; Jacobian Jac_Sur_TH;
                }

                Integral {
                  [thermalConductivityStiffness_<<k>>_<<l>>~{i}[{Ti~{i}~{j}~{<<nr + 1>>}}, {Ti~{i+1}~{j}~{<<nr + 1>>}}, delta~{i}[]] *
                    Dof{Ti~{i + <<k>> - 1}~{j}~{<<nr + 1>>}} , {Ti~{i + <<l>> - 1}~{j}~{<<nr + 1>>}} ];
                  In intDomain~{j}~{<<nr + 1>>}; Integration Int_line_TH; Jacobian Jac_Sur_TH;
                }

                Integral {
                  DtDof[ specificHeatCapacity_<<k>>_<<l>>~{i}[{Ti~{i}~{j}~{<<nr + 1>>}}, {Ti~{i+1}~{j}~{<<nr + 1>>}}, delta~{i}[]] *
                    Dof{Ti~{i + <<k>> - 1}~{j}~{<<nr + 1>>}} , {Ti~{i + <<l>> - 1}~{j}~{<<nr + 1>>}} ];
                  In intDomain~{j}~{<<nr + 1>>}; Integration Int_line_TH; Jacobian Jac_Sur_TH;
                }

                {% endfor %}

              {% endfor %}
            EndFor  // j
          EndFor  // i
        {% endfor %}

        {% for nr, n_ele in enumerate(rm_TH.thin_shells.quench_heaters.layers_number) %}
        {% set qu_nr = nr + len(rm_TH.thin_shells.insulation_types.thin_shells) %}

          For i In {0:<<n_ele-1>>} // loop over 1D FE elements
            For j In {1:2} // separation between vertical and horizontal
              {% for k in range(1,3) %}

                Integral { [- powerDensity_<<k>>~{i}[{Ti~{i}~{j}~{<<qu_nr + 1>>}}, {Ti~{i+1}~{j}~{<<qu_nr + 1>>}}, delta~{i}[]], {Ti~{i + <<k>> - 1}~{j}~{<<qu_nr + 1>>}} ];
                  In intDomain~{j}~{<<qu_nr + 1>>}; Integration Int_line_TH; Jacobian Jac_Sur_TH; }

              {% endfor %}
            EndFor  // j
          EndFor  // i
        {% endfor %}

        // one fewer for loop cause no horVerLayers --> but one more bc of function for N_eleL
        If (num_robin > 0)
          {% for nr, n_ele in enumerate(TSAinsulationAndQH_layers_number) %}
            // ----------------- ROBIN -----------------------------------------------
            For j In {1:2} // separation between vertical and horizontal
              For x In {1:2}
                For a In {1:2}
                 Integral { [heatExchCoeff[{Ti~{outerElem~{j}~{x}~{a}~{<<nr + 1>>}}~{j}~{<<nr + 1>>}}, Tinf[]] * Dof{Ti~{outerElem~{j}~{x}~{a}~{<<nr + 1>>}}~{j}~{<<nr + 1>>}},
                   {Ti~{outerElem~{j}~{x}~{a}~{<<nr + 1>>}}~{j}~{<<nr + 1>>}} ] ;
                   In bndRobinInt~{j}~{x}~{a}~{<<nr + 1>>}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }

                  Integral { [-heatExchCoeff[{Ti~{outerElem~{j}~{x}~{a}~{<<nr + 1>>}}~{j}~{<<nr + 1>>}}, Tinf[]] * Tinf[], {Ti~{outerElem~{j}~{x}~{a}~{<<nr + 1>>}}~{j}~{<<nr + 1>>}} ] ;
                    In bndRobinInt~{j}~{x}~{a}~{<<nr + 1>>}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }
                EndFor
              EndFor
            EndFor
          {% endfor %}
        EndIf

        // ----------------- NEUMANN -----------------------------------------------
        // one fewer for loop cause no horVerLayers --> but one more bc of function for N_eleL
        If (num_neumann > 0)
          {% for nr, n_ele in enumerate(TSAinsulationAndQH_layers_number) %}
            // ----------------- Neumann -----------------------------------------------
            For j In {1:2} // separation between vertical and horizontal
              For x In {1:2}
                For a In {1:2}
                  Integral { [-heatFlux[],
                    {Ti~{outerElem~{j}~{x}~{a}~{<<nr + 1>>}}~{j}~{<<nr + 1>>}} ] ;
                    In bndNeuInt~{j}~{x}~{a}~{<<nr + 1>>}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }
                EndFor
              EndFor
            EndFor
          {% endfor %}
        EndIf

      {% else %} {# not TSA #}

        // Neumann
        {% for nr, value in enumerate(rm_TH.boundaries.thermal.heat_flux.bc.value) %}
          Integral { [- <<value>> , {T} ] ;
            In {% if dm.magnet.solve.thermal.He_cooling.sides != 'external' and nr == 0 %} general_adiabatic {% else %} <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.heat_flux)[nr - 1 if dm.magnet.solve.thermal.He_cooling.sides != 'external' else nr]>> {% endif %}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }
        {% endfor %}

        // Robin
        // n * kappa grad (T) = h (T - Tinf) becomes two terms since GetDP can only
        // handle linear and not affine terms
        // NOTE: signs might be switched
        {% for nr, values in enumerate(rm_TH.boundaries.thermal.cooling.bc.values) %}
          {% if isinstance(values[0], str) %}
            Integral { [<<values[0]>>[{T}, <<values[1]>>] * Dof{T}, {T} ] ;
            In {% if dm.magnet.solve.thermal.He_cooling.enabled and nr == 0 %} general_cooling {% else %} <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.cooling)[nr - 1 if dm.magnet.solve.thermal.He_cooling.enabled else nr]>> {% endif %}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }
            Integral { [-<<values[0]>>[{T}, <<values[1]>>] * <<values[1]>> , {T} ] ;
            In {% if dm.magnet.solve.thermal.He_cooling.enabled and nr == 0 %} general_cooling {% else %} <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.cooling)[nr - 1 if dm.magnet.solve.thermal.He_cooling.enabled else nr]>> {% endif %}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }
          {% else %}
            Integral { [<<values[0]>> * Dof{T}, {T} ] ;
            In {% if dm.magnet.solve.thermal.He_cooling.enabled and nr == 0 %} general_cooling {% else %} <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.cooling)[nr - 1 if dm.magnet.solve.thermal.He_cooling.enabled else nr]>> {% endif %}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }
            Integral { [-<<values[0]>> * <<values[1]>> , {T} ] ;
            In {% if dm.magnet.solve.thermal.He_cooling.enabled and nr == 0 %} general_cooling {% else %} <<list(dm.magnet.solve.thermal.overwrite_boundary_conditions.cooling)[nr - 1 if dm.magnet.solve.thermal.He_cooling.enabled else nr]>> {% endif %}; Integration Int_line_TH ; Jacobian Jac_Sur_TH ; }
          {% endif %}
        {% endfor %}
      {% endif %}
    }
  }
{% endif %}
}

Resolution {
  { Name resolution;
    System {
    {% if dm.magnet.solve.electromagnetics.solve_type %}
      { Name Sys_Mag; NameOfFormulation Magnetostatics_a_2D; NameOfMesh "<<mf['EM']>>"; }
    {% endif %}
    {% if dm.magnet.solve.thermal.solve_type %}
      { Name Sys_The; NameOfFormulation Thermal_T; NameOfMesh "<<mf['TH']>>"; }
    {% endif %}
    {% if (dm.magnet.solve.electromagnetics.solve_type and dm.magnet.solve.thermal.solve_type) %}
      { Name sys_Mag_projection; NameOfFormulation Projection_EM_to_TH; NameOfMesh "<<mf['TH']>>";}
    {% endif %}
    }
    Operation {
    {% if dm.magnet.solve.electromagnetics.solve_type %}
      InitSolution[Sys_Mag];
      IterativeLoopN[<<dm.magnet.solve.electromagnetics.non_linear_solver.max_iterations>>, <<dm.magnet.solve.electromagnetics.non_linear_solver.relaxation_factor>>,
        System { { Sys_Mag, <<dm.magnet.solve.electromagnetics.non_linear_solver.rel_tolerance>>, <<dm.magnet.solve.electromagnetics.non_linear_solver.abs_tolerance>>, Solution <<dm.magnet.solve.electromagnetics.non_linear_solver.norm_type>> } }
      ] { GenerateJac[Sys_Mag]; SolveJac[Sys_Mag]; }
      PostOperation[Map_a];
    {% endif %}

    {% if (dm.magnet.solve.electromagnetics.solve_type and dm.magnet.solve.thermal.solve_type) %}
      Generate[sys_Mag_projection]; Solve[sys_Mag_projection];
      SaveSolution[sys_Mag_projection]; //PostOperation[b_after_projection_pos];
    {% endif %}

  {% if dm.magnet.solve.thermal.solve_type %}
      SetExtrapolationOrder[0];
      InitSolution Sys_The; // init. the solution using init. constraints

    {% if dm.magnet.solve.electromagnetics.solve_type %}
      //PostOperation[b_thermal];
    {% endif %}

    {% if dm.magnet.postproc.thermal.output_time_steps_txt %}
      CreateDirectory["T_avg"];
    {% endif %}
    {% if dm.magnet.postproc.thermal.output_time_steps_txt == 1 %}
      PostOperation[T_avg];
    {% endif %}

    {% if dm.magnet.postproc.thermal.output_time_steps_pos == 1 %}
      PostOperation[Map_T];
    {% endif %}

      // initialized cumulate times to zero to avoid warning
      Evaluate[$tg_cumul_cpu = 0, $ts_cumul_cpu = 0, $tg_cumul_wall = 0, $ts_cumul_wall = 0];
      Print["timestep,gen_wall,gen_cpu,sol_wall,sol_cpu,pos_wall,pos_cpu,gen_wall_cumul,gen_cpu_cumul,sol_wall_cumul,sol_cpu_cumul,pos_wall_cumul,pos_cpu_cumul", File "computation_times.csv"];
      //PostOperation[b_after_projection_pos];
      
    {% if dm.magnet.solve.thermal.solve_type == 'transient' %}

      Evaluate[$tg_wall = 0, $tg_cpu = 0, $ts_wall = 0, $ts_cpu = 0];

      TimeLoopAdaptive
      [ <<dm.magnet.solve.thermal.time_stepping.initial_time>>, <<dm.magnet.solve.thermal.time_stepping.final_time>>, <<dm.magnet.solve.thermal.time_stepping.initial_time_step>>, <<dm.magnet.solve.thermal.time_stepping.min_time_step>>, <<dm.magnet.solve.thermal.time_stepping.max_time_step>>, "<<dm.magnet.solve.thermal.time_stepping.integration_method>>", List[Breakpoints],
      System { { Sys_The, <<dm.magnet.solve.thermal.time_stepping.rel_tol_time>>, <<dm.magnet.solve.thermal.time_stepping.abs_tol_time>>, <<dm.magnet.solve.thermal.time_stepping.norm_type>> } } ]
      {
        IterativeLoopN[<<dm.magnet.solve.thermal.non_linear_solver.max_iterations>>, <<dm.magnet.solve.thermal.non_linear_solver.relaxation_factor>>,
          System { { Sys_The, <<dm.magnet.solve.thermal.non_linear_solver.rel_tolerance>>, <<dm.magnet.solve.thermal.non_linear_solver.abs_tolerance>>, Solution <<dm.magnet.solve.thermal.non_linear_solver.norm_type>> } }]
        {
          Evaluate[ $tg1_wall = GetWallClockTime[], $tg1_cpu = GetCpuTime[] ];
          GenerateJac Sys_The ;
          Evaluate[ $tg2_wall = GetWallClockTime[], $tg2_cpu = GetCpuTime[] ];

          // add to generation times of previous rejected time steps
          Evaluate[ $tg_wall = $tg_wall + $tg2_wall - $tg1_wall, $tg_cpu = $tg_cpu + $tg2_cpu - $tg1_cpu ];

          Evaluate[ $ts1_wall = GetWallClockTime[], $ts1_cpu = GetCpuTime[] ];
          SolveJac Sys_The;
          Evaluate[ $ts2_wall = GetWallClockTime[], $ts2_cpu = GetCpuTime[] ];

          // add to solution times of previous rejected time steps
          Evaluate[ $ts_wall = $ts_wall + $ts2_wall - $ts1_wall, $ts_cpu = $ts_cpu + $ts2_cpu - $ts1_cpu ];

        {% if dm.magnet.solve.thermal.enforce_init_temperature_as_minimum %}
          SolutionSetMin[Sys_The, <<dm.magnet.solve.thermal.init_temperature>>];
        {% endif %}
        }
      }
      {
        // save solution to .res file
        SaveSolution[Sys_The];

        Evaluate[ $tp1_wall = GetWallClockTime[], $tp1_cpu = GetCpuTime[] ];
        // print average temperature
      {% if (not dm.magnet.postproc.thermal.save_txt_at_the_end and dm.magnet.postproc.thermal.output_time_steps_txt) %}
        {% if dm.magnet.postproc.thermal.output_time_steps_txt > 1%}
        Test[$TimeStep > 1] {
          PostOperation[T_avg];
        }
        {% else %}
        PostOperation[T_avg];
        {% endif %}
      {% endif %}

        // print temperature map
      {% if (not dm.magnet.postproc.thermal.save_pos_at_the_end and dm.magnet.postproc.thermal.output_time_steps_pos) %}
        {% if dm.magnet.postproc.thermal.output_time_steps_pos > 1%}
        Test[$TimeStep > 1] {
          PostOperation[Map_T];
        }
        {% else %}
        PostOperation[Map_T];
        {% endif %}
      {% endif %}

        PostOperation[PrintMaxTemp]; // save maximum temperature in register 1
        Evaluate[ $tp2_wall = GetWallClockTime[], $tp2_cpu = GetCpuTime[] ];

        Evaluate[ $tp_wall = $tp2_wall - $tp1_wall, $tp_cpu = $tp2_cpu - $tp1_cpu ];

        // cumulated times
        Evaluate[ $tg_cumul_wall = $tg_cumul_wall + $tg_wall, $tg_cumul_cpu = $tg_cumul_cpu + $tg_cpu, $ts_cumul_wall = $ts_cumul_wall + $ts_wall, $ts_cumul_cpu = $ts_cumul_cpu + $ts_cpu, $tp_cumul_wall = $tp_cumul_wall + $tp2_wall - $tp1_wall, $tp_cumul_cpu = $tp_cumul_cpu + $tp2_cpu - $tp1_cpu];

        // print to file
        Print[{$TimeStep, $tg_wall, $tg_cpu, $ts_wall, $ts_cpu, $tp_wall, $tp_cpu, $tg_cumul_wall, $tg_cumul_cpu, $ts_cumul_wall, $ts_cumul_cpu, $tp_cumul_wall, $tp_cumul_cpu}, Format "%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g", File "computation_times.csv"];

        // reset after accepted time step
        Evaluate[$tg_wall = 0, $tg_cpu = 0, $ts_wall = 0, $ts_cpu = 0];

        // check if maximum temperature is reached

      {# raw block needed since use of # in following code #}
      {% raw %}
        Print[{#1}, Format "Maximum temperature: %g "];
        Test[#1 > stop_temperature] {
          Break[];
        }
      {% endraw %}
      }
    
    {% else %}  // stationary

      Evaluate[$tg_wall = 0, $tg_cpu = 0, $ts_wall = 0, $ts_cpu = 0];

      IterativeLoopN[<<dm.magnet.solve.thermal.non_linear_solver.max_iterations>>, <<dm.magnet.solve.thermal.non_linear_solver.relaxation_factor>>,
        System { { Sys_The, <<dm.magnet.solve.thermal.non_linear_solver.rel_tolerance>>, <<dm.magnet.solve.thermal.non_linear_solver.abs_tolerance>>, Solution <<dm.magnet.solve.thermal.non_linear_solver.norm_type>> } }]
      {
        Evaluate[ $tg1_wall = GetWallClockTime[], $tg1_cpu = GetCpuTime[] ];
        GenerateJac Sys_The ;
        Evaluate[ $tg2_wall = GetWallClockTime[], $tg2_cpu = GetCpuTime[] ];

        // add to generation times of previous rejected time steps
        Evaluate[ $tg_wall = $tg_wall + $tg2_wall - $tg1_wall, $tg_cpu = $tg_cpu + $tg2_cpu - $tg1_cpu ];

        Evaluate[ $ts1_wall = GetWallClockTime[], $ts1_cpu = GetCpuTime[] ];
        SolveJac Sys_The;
        Evaluate[ $ts2_wall = GetWallClockTime[], $ts2_cpu = GetCpuTime[] ];

        // add to solution times of previous rejected time steps
        Evaluate[ $ts_wall = $ts_wall + $ts2_wall - $ts1_wall, $ts_cpu = $ts_cpu + $ts2_cpu - $ts1_cpu ];

      {% if dm.magnet.solve.thermal.enforce_init_temperature_as_minimum %}
        SolutionSetMin[Sys_The, <<dm.magnet.solve.thermal.init_temperature>>];
      {% endif %}
      }

      // cumulated times
      Evaluate[ $tg_cumul_wall = $tg_cumul_wall + $tg_wall, $tg_cumul_cpu = $tg_cumul_cpu + $tg_cpu, $ts_cumul_wall = $ts_cumul_wall + $ts_wall, $ts_cumul_cpu = $ts_cumul_cpu + $ts_cpu ];

      // print to file
      Print[{$TimeStep, $tg_wall, $tg_cpu, $ts_wall, $ts_cpu, $tp_wall, $tp_cpu, $tg_cumul_wall, $tg_cumul_cpu, $ts_cumul_wall, $ts_cumul_cpu, $tp_cumul_wall, $tp_cumul_cpu}, Format "%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g,%g", File "computation_times.csv"];

      SaveSolution[Sys_The];
    {% endif %}

      Evaluate[ $tp1_wall = GetWallClockTime[], $tp1_cpu = GetCpuTime[] ];
    {% if (dm.magnet.postproc.thermal.save_txt_at_the_end and dm.magnet.postproc.thermal.output_time_steps_txt) %}
      PostOperation[T_avg];
    {% endif %}

    {% if (dm.magnet.postproc.thermal.save_pos_at_the_end and dm.magnet.postproc.thermal.output_time_steps_pos) %}
      PostOperation[Map_T];
    {% endif %}
      Evaluate[ $tp2_wall = GetWallClockTime[], $tp2_cpu = GetCpuTime[] ];

      Evaluate[ $tp_wall = $tp2_wall - $tp1_wall, $tp_cpu = $tp2_cpu - $tp1_cpu ];

      Print[{$tp_wall, $tp_cpu, $tg_cumul_wall, $tg_cumul_cpu, $ts_cumul_wall, $ts_cumul_cpu, $tp_cumul_wall, $tp_cumul_cpu}, Format "-1,0,0,0,0,%g,%g,%g,%g,%g,%g,%g,%g", File "computation_times.csv"];
  {% endif %}
    }
  }
}

PostProcessing {
{% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name MagSta_a_2D; NameOfFormulation Magnetostatics_a_2D; NameOfSystem Sys_Mag;
    Quantity {
      { Name a;
        Value {
          Term { [ {a} ]; In <<nc.omega>>_EM; Jacobian Jac_Vol_EM; }
        }
      }
      { Name az;
        Value {
          Term { [ CompZ[{a}] ]; In <<nc.omega>>_EM; Jacobian Jac_Vol_EM; }
        }
      }
      { Name b;
        Value {
          Term { [ {d a} ]; In <<nc.omega>>_EM; Jacobian Jac_Vol_EM; }
        }
      }
      { Name h;
        Value {
          Term { [ nu[{d a}] * {d a} ]; In <<nc.omega>>_EM; Jacobian Jac_Vol_EM; }
        }
      }
      { Name js;
        Value {
          Term { [ {js} ]; In <<nc.omega>>_EM; Jacobian Jac_Vol_EM; }
        }
      }
    }
  }
{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}
  { Name Thermal_T ; NameOfFormulation Thermal_T ; NameOfSystem Sys_The ;
    PostQuantity {
      // Temperature
      { Name T ;
        Value {
          Local { [ {T} ] ;
            In <<nc.omega>>_TH ; Jacobian Jac_Vol_TH ; }
        }
      }

      { Name jOverJc ;
        Value {
          {% if dm.magnet.solve.electromagnetics.solve_type %}
          Term { [ source_current/area_fct[] * 1/(criticalCurrentDensity[{T}, GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] + 1) ] ;
            In <<nc.omega>>_TH ; Jacobian Jac_Vol_TH ; }
          {% else %}
          Term { [ source_current/area_fct[] * 1/(criticalCurrentDensity[{T}] + 1) ] ;
            In <<nc.omega>>_TH ; Jacobian Jac_Vol_TH ; }
          {% endif %}
        }
      }

      // Temperature average as integral quantity
      { Name T_avg ;
        Value {
          Integral {  [ {T} / area_fct[] ] ;
            In Region[ {<<nc.omega>><<nc.powered>>_TH{% if dm.magnet.geometry.thermal.with_iron_yoke %}, <<nc.omega>><<nc.iron>>{% endif %}{% if dm.magnet.geometry.thermal.with_wedges %}, <<nc.omega>><<nc.induced>>_TH{% endif %} } ] ; Jacobian Jac_Vol_TH ; Integration Int_conducting_TH; }

        {% if not dm.magnet.geometry.thermal.use_TSA %}
          Integral {  [ {T} / area_fct[] ] ;
            In <<nc.omega>><<nc.insulator>>_TH ; Jacobian Jac_Vol_TH ; Integration Int_insulating_TH; }
        {% endif %}
        }
      }

    {% if dm.magnet.solve.electromagnetics.solve_type %}
      { Name b_thermal ;
        Value {
          Local {  [GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] ;
            In <<nc.omega>><<nc.powered>>_TH ; Jacobian Jac_Vol_TH ; }
        }
      }
    {% endif %}

    { Name rho ;
      Value {
        {% if dm.magnet.solve.electromagnetics.solve_type %}
          Term { [ rho[{T}, GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] ] ;
        {% else %}
          Term { [ rho[{T}] ] ;
        {% endif %}
          In <<nc.omega>><<nc.powered>>_TH ; Jacobian Jac_Vol_TH ; }
      }
    }
    }
  }

  {% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name post_projection; NameOfFormulation Projection_EM_to_TH; NameOfSystem sys_Mag_projection;
    PostQuantity {
      { Name b_before_projection ;
        Value {
          Term {  [Norm[{d a_before_projection}]] ;
            In <<nc.omega>><<nc.powered>>_TH ; Jacobian Jac_Vol_TH ; }
        }
      }
      { Name b_after_projection ;
        Value {
          Term {  [GetVariable[ElementNum[], QuadraturePointIndex[]]{$Bnorm}] ;
            In <<nc.omega>><<nc.powered>>_TH ; Jacobian Jac_Vol_TH ; }
        }
      }
    }
  }
  {% endif %}
{% endif %}
}

{% if dm.magnet.solve.thermal.solve_type %}
PostOperation PrintMaxTemp UsingPost Thermal_T {
  // Get maximum in bare region and store in register 1
  Print[ T, OnElementsOf <<nc.omega>>_TH, StoreMaxInRegister 1, Format Table,
    LastTimeStepOnly 1, SendToServer "No"] ;
}
{% endif %}

PostOperation {
  { Name Dummy; NameOfPostProcessing {% if dm.magnet.solve.thermal.solve_type %} Thermal_T {% else %} MagSta_a_2D {% endif %};
    Operation { }
  }

{% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name Map_a; NameOfPostProcessing MagSta_a_2D;
    Operation {
    {% for var_name, vol_name in zip(dm.magnet.postproc.electromagnetics.variables, dm.magnet.postproc.electromagnetics.volumes) %}
      Print[ <<var_name>>, OnElementsOf <<vol_name>>_EM, File "<<var_name>>_<<vol_name>>.pos"] ;
    {% endfor %}
	  //Print [ b, OnLine {{List[{0,0,0}]}{List[{<<rm_EM.air_far_field.vol.radius_out>>,0,0}]}} {1000}, Format SimpleTable, File "Center_line.csv"];
    }
  }
{% endif %}

{% if dm.magnet.solve.thermal.solve_type %}
  {% if dm.magnet.solve.electromagnetics.solve_type %}
  { Name b_thermal; NameOfPostProcessing Thermal_T;
    Operation {
      Print[ b_thermal, OnElementsOf <<nc.omega>><<nc.powered>>_TH, File "b_thermal.pos"] ;
    }
  }
  { Name b_after_projection_pos; NameOfPostProcessing post_projection;
    Operation {
      Print[ b_before_projection, OnElementsOf <<nc.omega>><<nc.powered>>_TH, File "b_before_projection_gmsh.pos"] ;
      Print[ b_after_projection, OnElementsOf <<nc.omega>><<nc.powered>>_TH, File "b_after_projection.pos"] ;
    }
  }
  {% endif %}

  { Name Map_T; NameOfPostProcessing Thermal_T;
  {% if dm.magnet.postproc.thermal.output_time_steps_pos > 1 %}
    {% set resample_step = (dm.magnet.solve.thermal.time_stepping.final_time - dm.magnet.solve.thermal.time_stepping.initial_time)/dm.magnet.postproc.thermal.output_time_steps_pos %}
    {% set last_time_step_only = 0 %}
    ResampleTime[<<dm.magnet.solve.thermal.time_stepping.initial_time>>, <<dm.magnet.solve.thermal.time_stepping.final_time>>, <<resample_step>>];
  {% elif (dm.magnet.postproc.thermal.output_time_steps_pos == 1 and not dm.magnet.postproc.thermal.save_pos_at_the_end) %}
    {% set last_time_step_only = 1 %}
  {% else %}
    {% set last_time_step_only = 0 %}
  {% endif %}
    Operation {
    {% for var_name, vol_name in zip(dm.magnet.postproc.thermal.variables, dm.magnet.postproc.thermal.volumes) %}
      Print[ <<var_name>>, OnElementsOf <<vol_name>>_TH, File "<<var_name>>_<<vol_name>>.pos", SendToServer "No", LastTimeStepOnly <<last_time_step_only>>, AppendToExistingFile <<last_time_step_only>> ] ;
    {% endfor %}
      //Print[ JoverJc, OnElementsOf <<nc.omega>><<nc.powered>>_TH, File "JoverJc_<<nc.omega>><<nc.powered>>.pos", SendToServer "No", LastTimeStepOnly <<last_time_step_only>>, AppendToExistingFile <<last_time_step_only>>, AtGaussPoints 4, Depth 0 ] ;
      //Print[ rho, OnElementsOf <<nc.omega>><<nc.powered>>_TH, File "rho_<<nc.omega>><<nc.powered>>.pos", SendToServer "No", LastTimeStepOnly <<last_time_step_only>>, AppendToExistingFile <<last_time_step_only>> ] ;
    }
  }

  { Name T_avg; NameOfPostProcessing Thermal_T;
  {% if dm.magnet.postproc.thermal.output_time_steps_txt > 1 %}
    {% set resample_step = (dm.magnet.solve.thermal.time_stepping.final_time - dm.magnet.solve.thermal.time_stepping.initial_time)/dm.magnet.postproc.thermal.output_time_steps_txt %}
    {% set last_time_step_only = 0 %}
    ResampleTime[<<dm.magnet.solve.thermal.time_stepping.initial_time>>, <<dm.magnet.solve.thermal.time_stepping.final_time>>, <<resample_step>>];
  {% elif (dm.magnet.postproc.thermal.output_time_steps_txt == 1 and not dm.magnet.postproc.thermal.save_txt_at_the_end) %}
    {% set last_time_step_only = 1 %}
  {% else %}
    {% set last_time_step_only = 0 %}
  {% endif %}
    Operation {
    // writes pairs of time step and average temperature to file, one line for each time step
    {% for idx, half_turn in enumerate(rm_TH.powered['r1_a1'].vol.numbers + rm_TH.powered['r2_a1'].vol.numbers + rm_TH.powered['r1_a2'].vol.numbers + rm_TH.powered['r2_a2'].vol.numbers) %}
      Print[ T_avg[Region[<<half_turn>>]], OnGlobal, File "T_avg/T_avg_<<idx>>.txt", Format Table, SendToServer "No", LastTimeStepOnly <<last_time_step_only>>, AppendToExistingFile <<last_time_step_only>>] ;
    {% endfor %}
    }
  }
{% endif %}
}
