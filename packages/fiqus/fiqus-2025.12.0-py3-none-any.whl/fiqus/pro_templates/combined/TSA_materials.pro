// Quench Heater Circuits:
{% macro MATERIAL_QuenchHeater_SSteel_t_T(t_on="None", U_0="None", C="None", R_warm="None", w_SS="None", h_SS="None", l_SS="None", mode="None", time="$Time", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None") -%}
TSA_CFUN_QHCircuit_t_T_rhs[<<time>>, <<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<t_on>>, <<U_0>>, <<C>>, <<R_warm>>, <<w_SS>>, <<h_SS>>, <<l_SS>>, <<mode>>, <<k>>, <<GaussianPoints>>}
{%- endmacro %} // mode: 1 -> Power, 2 -> Current, 3 -> Resistance

// Thermal Conductivities Stiffness:
{% macro MATERIAL_ThermalConductivity_Copper_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kCu_T_constantThickness_stiffness[<<T_i>>, <<T_iPlusOne>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kCu_T_stiffness[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Kapton_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kKapton_T_constantThickness_stiffness[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kKapton_T_stiffness[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Stycast_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kStycast_T_constantThickness_stiffness[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kStycast_T_stiffness[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_G10_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kG10_T_constantThickness_stiffness[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kG10_T_stiffness[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_SSteel_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kSteel_T_constantThickness_stiffness[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kSteel_T_stiffness[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Indium_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kIn_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kIn_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

// Thermal Conductivities Mass:
{% macro MATERIAL_ThermalConductivity_Copper_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kCu_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kCu_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Kapton_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kKapton_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kKapton_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Stycast_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kStycast_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kStycast_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_G10_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kG10_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kG10_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_SSteel_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kSteel_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kSteel_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Indium_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_kIn_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_kIn_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

// Specific Heat Capacities:
{% macro MATERIAL_SpecificHeatCapacity_Copper_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_CvCu_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_CvCu_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Kapton_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_CvKapton_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_CvKapton_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{# no data in SMALI, constant value for now #}
{% macro MATERIAL_SpecificHeatCapacity_Stycast_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{# from rough calculations from www.sciencedirect.com/science/article/pii/S0011227521000874 #}
{%- if constantThickness %}
TSA_constantMaterial_constantThickness_mass[]{<<thickness_TSA>>, 192, <<k>>, <<l>>}
{%- else %}
TSA_constantMaterial_mass[<<thickness_TSA>>]{192, <<k>>, <<l>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_G10_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_CvG10_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_CvG10_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_SSteel_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_CvSteel_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_CvSteel_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Indium_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_CvIn_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_CvIn_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

// Resistivities Stiffness:
{% macro MATERIAL_Resistivity_Copper_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_rhoCu_T_constantThickness_stiffness[<<T_i>>, <<T_iPlusOne>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_rhoCu_T_stiffness[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}


{% macro MATERIAL_Resistivity_Indium_TSAStiffness_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_rhoIn_T_constantThickness_stiffness[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_rhoIn_T_stiffness[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

// Resistivities Mass:
{% macro MATERIAL_Resistivity_Copper_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_rhoCu_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_rhoCu_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<BMagnitude>>, <<RRR>>, <<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}

{% macro MATERIAL_Resistivity_Indium_TSAMass_T(RRR="5", RRRRefTemp="5", BMagnitude="5", T_i="", T_iPlusOne="", thickness_TSA="None", k="None", l="None", GaussianPoints="None", constantThickness=False) -%}
{%- if constantThickness %}
TSA_CFUN_rhoIn_T_constantThickness_mass[<<T_i>>, <<T_iPlusOne>>]{<<k>>, <<l>>, <<GaussianPoints>>, <<thickness_TSA>>}
{%- else %}
TSA_CFUN_rhoIn_T_mass[<<T_i>>, <<T_iPlusOne>>, <<thickness_TSA>>]{<<k>>, <<l>>, <<GaussianPoints>>}
{%- endif %}
{%- endmacro %}