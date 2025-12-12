// Quench Heater Circuits:
{% macro MATERIAL_QuenchHeater_SSteel_t_T(t_on="None", U_0="None", C="None", R_warm="None", w_SS="None", h_SS="None", l_SS="None", mode="None", time="$Time", T="$1") -%}
CFUN_QHCircuit_t_rhoSS[<<time>>, CFUN_rhoSS_T[<<T>>]]{<<t_on>>, <<U_0>>, <<C>>, <<R_warm>>, <<w_SS>>, <<h_SS>>, <<l_SS>>, <<mode>>}
{%- endmacro %} // mode: 1 -> Power, 2 -> Current, 3 -> Resistance

// Critical Currents:
{% macro MATERIAL_CriticalCurrent_NiobiumTitanium_T_B_a(area="SurfaceArea[]", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_IcNbTi_T_B_a[<<T>>, <<BMagnitude>>, <<area>>]
{%- endmacro %}
{% macro MATERIAL_CriticalCurrent_NiobiumTitanium_T_a(area="SurfaceArea[]", T="$1", BMagnitude="5") -%}
CFUN_IcNbTi_T_a[<<T>>, <<area>>]{<<BMagnitude>>}
{%- endmacro %}

// Critical Current Densities:
{% macro MATERIAL_CriticalCurrentDensity_NiobiumTitanium_CUDI1_T_B(C1="None", C2="None", Tc0="None", Bc20="None", wireDiameter="None", Cu_noCu="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_Jc_NbTi_Cudi_fit1_T_B[<<T>>, <<BMagnitude>>]{<<Tc0>>, <<Bc20>>, <<C1>>, <<C2>>, <<wireDiameter>>, <<Cu_noCu>>}
{%- endmacro %}
{% macro MATERIAL_CriticalCurrentDensity_NiobiumTitanium_CUDI1_T(C1="None", C2="None", Tc0="None", Bc20="None", wireDiameter="None", Cu_noCu="None", T="$1", BMagnitude="5") -%}
CFUN_Jc_NbTi_Cudi_fit1_T[<<T>>]{<<BMagnitude>>, <<Tc0>>, <<Bc20>>, <<C1>>, <<C2>>, <<wireDiameter>>, <<Cu_noCu>>}
{%- endmacro %}

{% macro MATERIAL_CriticalCurrentDensity_Niobium3Tin_Summers_T_B(Jc0="None", Tc0="None", Bc20="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_Jc_Nb3Sn_Summers_T_B[<<T>>, <<BMagnitude>>]{<<Jc0>>, <<Tc0>>, <<Bc20>>}
{%- endmacro %}
{% macro MATERIAL_CriticalCurrentDensity_Niobium3Tin_Summers_T(Jc0="None", Tc0="None", Bc20="None", T="$1", BMagnitude="5") -%}
CFUN_Jc_Nb3Sn_Summers_T[<<T>>]{<<BMagnitude>>, <<Jc0>>, <<Tc0>>, <<Bc20>>}
{%- endmacro %}

{% macro MATERIAL_CriticalCurrentDensity_Niobium3Tin_Bordini_T_B(Tc0="None", Bc20="None", C0="None", alpha="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_Jc_Bordini_T_B[<<T>>, <<BMagnitude>>]{<<Tc0>>, <<Bc20>>, <<C0>>, <<alpha>>}
{%- endmacro %}
{% macro MATERIAL_CriticalCurrentDensity_Niobium3Tin_Bordini_T(Tc0="None", Bc20="None", C0="None", alpha="None", T="$1", BMagnitude="5") -%}
CFUN_Jc_Bordini_T[<<T>>]{<<BMagnitude>>, <<Tc0>>, <<Bc20>>, <<C0>>, <<alpha>>}
{%- endmacro %}

{% macro MATERIAL_CriticalCurrentDensity_BSCCO2212_BSCCO_2212_LBNL_T_B(f_scaling="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_Jc_T_B_BSCCO2212_block20T_new_T_B[<<T>>, <<BMagnitude>>]{<<f_scaling>>}
{%- endmacro %}
{% macro MATERIAL_CriticalCurrentDensity_BSCCO2212_BSCCO_2212_LBNL_T(f_scaling="None", T="$1", BMagnitude="5") -%}
CFUN_Jc_T_B_BSCCO2212_block20T_new_T[<<T>>]{<<BMagnitude>>, <<f_scaling>>}
{%- endmacro %}

// Resistivities:
{% macro MATERIAL_Resistivity_Copper_T_B(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_rhoCu_T_B[<<T>>, <<BMagnitude>>]{<<RRR>>}
{%- endmacro %}
{% macro MATERIAL_Resistivity_Copper_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_rhoCu_T[<<T>>]{<<BMagnitude>>, <<RRR>>}
{%- endmacro %}

{% macro MATERIAL_Resistivity_Hastelloy_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_rhoHast_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_Resistivity_Silver_T_B(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_rhoAg_T_B[<<T>>, <<BMagnitude>>]{<<RRR>>, <<RRRRefTemp>>}
{%- endmacro %}
{% macro MATERIAL_Resistivity_Silver_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_rhoAg_T[<<T>>]{<<BMagnitude>>, <<RRR>>, <<RRRRefTemp>>}
{%- endmacro %}

{% macro MATERIAL_Resistivity_Indium_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_rhoIn_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_Resistivity_SSteel_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_rhoSS_T[<<T>>]
{%- endmacro %}

// Thermal Conductivities:
{% macro MATERIAL_ThermalConductivity_Copper_T_B(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_kCu_T_rho0_rho[<<T>>, CFUN_rhoCu_T[<<T>>]{0, <<RRR>>}, CFUN_rhoCu_T_B[<<T>>, <<BMagnitude>>]{<<RRR>>}]{<<RRR>>}
{%- endmacro %}
{% macro MATERIAL_ThermalConductivity_Copper_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_kCu_T_rho0_rho[<<T>>, CFUN_rhoCu_T[<<T>>]{0, <<RRR>>}, CFUN_rhoCu_T[<<T>>]{<<BMagnitude>>, <<RRR>>}]{<<RRR>>}
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Hastelloy_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_kHast_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Silver_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_kAg_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Indium_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_kIn_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_SSteel_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_kSteel_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_Kapton_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_kKapton_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_ThermalConductivity_G10_T(RRR="None", RRRRefTemp="None", T="$1", BMagnitude="5") -%}
CFUN_kG10_T[<<T>>]
{%- endmacro %}

// Specific Heat Capacities:
{% macro MATERIAL_SpecificHeatCapacity_NiobiumTitanium_T_B(C1="None", C2="None", current="None", T="$1", BMagnitude="Norm[$2]") -%}
CFUN_CvNbTi_T_B[<<T>>, <<BMagnitude>>]{<<current>>, <<C1>>, <<C2>>}
{%- endmacro %}
{% macro MATERIAL_SpecificHeatCapacity_NiobiumTitanium_T(C1="None", C2="None", current="None", T="$1", BMagnitude="5") -%}
CFUN_CvNbTi_T[<<T>>]{<<BMagnitude>>, <<current>>, <<C1>>, <<C2>>}
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Niobium3Tin_T_B(T="$1", BMagnitude="Norm[$2]") -%}
CFUN_CvNb3Sn_T_B[<<T>>, <<BMagnitude>>]
{%- endmacro %}
{% macro MATERIAL_SpecificHeatCapacity_Niobium3Tin_T(T="$1", BMagnitude="5") -%}
CFUN_CvNb3Sn_T[<<T>>]{<<BMagnitude>>}
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_BSCCO2212_T(T="$1") -%}
CFUN_CvBSCCO2212_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Copper_T(T="$1") -%}
CFUN_CvCu_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Hastelloy_T(T="$1") -%}
CFUN_CvHast_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Silver_T(T="$1") -%}
CFUN_CvAg_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Indium_T(T="$1") -%}
CFUN_CvIn_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_SSteel_T(T="$1") -%}
CFUN_CvSteel_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Kapton_T(T="$1") -%}
CFUN_CvKapton_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_G10_T(T="$1") -%}
CFUN_CvG10_T[<<T>>]
{%- endmacro %}

{% macro MATERIAL_SpecificHeatCapacity_Helium_T(T="$1") -%}
CFUN_CvHe_T[<<T>>]
{%- endmacro %}