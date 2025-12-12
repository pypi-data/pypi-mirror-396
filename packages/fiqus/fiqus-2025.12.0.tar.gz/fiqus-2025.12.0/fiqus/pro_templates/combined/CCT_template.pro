Group {
{% for name, number in zip(rm.powered['cct'].vol.names, rm.powered['cct'].vol.numbers) %}
  <<name>> = Region[{<<number>>}];
{% endfor %}
{% for name, number in zip(rm.powered['cct'].surf_in.names, rm.powered['cct'].surf_in.numbers) %}
  <<name>> = Region[{<<number>>}];
{% endfor %}
{% for name, number in zip(rm.powered['cct'].surf_out.names, rm.powered['cct'].surf_out.numbers) %}
  <<name>> = Region[{<<number>>}];
{% endfor %}
{% for name, number in zip(rm.induced['cct'].vol.names, rm.induced['cct'].vol.numbers) %}
  <<name>> = Region[{<<number>>}];
{% endfor %}
  <<nc.omega>><<nc.cond>> = Region[{<<(rm.powered['cct'].vol.numbers+rm.induced['cct'].vol.numbers)|join(', ')>>}];
  //<<nc.line>><<nc.air>> = Region[{<<rm.air.line.number>>}];
  //<<nc.omega>><<nc.air>> = Region[{<<([rm.air.vol.number]+[rm.air.line.number])|join(', ')>>}];
  <<nc.omega>><<nc.air>> = Region[{<<rm.air.vol.number>>}];
  <<nc.omega>> = Region[{<<(rm.powered['cct'].vol.numbers+rm.induced['cct'].vol.numbers+[rm.air.vol.number])|join(', ')>>}];
  <<nc.terms>> = Region[{<<rm.powered['cct'].surf_in.numbers|join(', ')>>, <<rm.powered['cct'].surf_out.numbers|join(', ')>>}];
  <<nc.bd>><<nc.omega>> = Region[{<< rm.air.surf.number>>, << rm.powered['cct'].surf_in.numbers|join(', ')>>, << rm.powered['cct'].surf_out.numbers|join(', ')>>}];
  <<nc.omega>><<nc.powered>> = Region[{<<rm.powered['cct'].vol.numbers|join(', ')>>}];
  

  {% for name, number in zip(rm.powered['cct'].cochain.names, rm.powered['cct'].cochain.numbers) %}
  DefineConstant[ <<name>> = {<<number>>, Min 1, Step 1, Closed 1,
      Name "Cohomology/<<name>>"} ];
  <<name>> = Region[{<<name>>}];
  {% endfor %}
  Cuts<<nc.powered>> = Region[ {<<rm.powered['cct'].cochain.names|join(', ')>>} ];
  {% for name, number in zip(rm.induced['cct'].cochain.names, rm.induced['cct'].cochain.numbers) %}
  DefineConstant[ <<name>> = {<<number>>, Min 1, Step 1,
      Name "Cohomology/<<name>>"} ];
  <<name>> = Region[{<<name>>}];
  {% endfor %}
  Cuts<<nc.induced>> = Region[ {<<rm.induced['cct'].cochain.names|join(', ')>>} ];
  DomainDummy = Region[ 12345 ] ; // Dummy region number for postpro with functions
}
Function {
  mesh_file = "<<mf>>";
  DefineConstant
  [
	{% for vol_name, current in zip(rm.powered['cct'].vol.names, rm.powered['cct'].vol.currents) %}
    I_<<vol_name>> = {<<current>>, Step 1, Name "Powering/<<vol_name>>_Current [A]"},
	{% endfor %}
	{% for vol_name, sigma, mu_r in zip(rm.powered['cct'].vol.names, rm.powered['cct'].vol.sigmas, rm.powered['cct'].vol.mu_rs) %}
    <<vol_name>>_Conductivity  = {<<sigma>>, Min 0, Step 1e6, Name "Materials/<<vol_name>> Cond. [S per m]"},
	<<vol_name>>_Permeability  = {<<mu_r>>, Min 0, Step 1e1, Name "Materials/<<vol_name>> Rel. Perm. [-]"},
	{% endfor %}
	{% for vol_name, sigma, mu_r in zip(rm.induced['cct'].vol.names, rm.induced['cct'].vol.sigmas, rm.induced['cct'].vol.mu_rs) %}
    <<vol_name>>_Conductivity  = {<<sigma>>, Min 0, Step 1e6, Name "Materials/<<vol_name>> Cond. [S per m]"},
	<<vol_name>>_Permeability  = {<<mu_r>>, Min 0, Step 1e1, Name "Materials/<<vol_name>> Rel. Perm. [-]"},
	{% endfor %}
	<<rm.air.vol.name>>_Conductivity  = {<<rm.air.vol.sigma>>, Min 0, Step 1e6, Name "Materials/<<rm.air.vol.name>> Cond. [S per m]"},
	<<rm.air.vol.name>>_Permeability  = {<<rm.air.vol.mu_r>>, Min 0, Step 1e1, Name "Materials/<<rm.air.vol.name>> Rel. Perm. [-]"}
  ];
  mu0 = 4*Pi*1e-7; 				// Vacuum permeability
  nu []  = 1./mu0;
{% for vol_name in rm.powered['cct'].vol.names %}
  I_<<vol_name>>[] = I_<<vol_name>>;
  sigma[<<vol_name>>] = <<vol_name>>_Conductivity;
  mu[<<vol_name>>] = mu0*<<vol_name>>_Permeability;
{% endfor %}
{% for vol_name in rm.induced['cct'].vol.names %}
  sigma[<<vol_name>>] = <<vol_name>>_Conductivity;
  mu[<<vol_name>>] = mu0*<<vol_name>>_Permeability;
{% endfor %}
  sigma[<<nc.omega>><<nc.air>>] = <<rm.air.vol.name>>_Conductivity;			// Air
  mu[<<nc.omega>><<nc.air>>] = mu0*<<rm.air.vol.name>>_Permeability;  		// Air
}
Jacobian {
  { Name Vol ;
    Case { { Region All ; Jacobian Vol ; } }
  }
  { Name Sur ;
    Case { { Region All ; Jacobian Sur ; } }
  }
  { Name Lin ;
    Case { { Region All ; Jacobian Lin ; } }
  }
}

Integration {
    { Name Int ;
        Case {
            { Type Gauss ;
                Case {
                    { GeoElement Point ; NumberOfPoints 1 ; }
                    { GeoElement Line ; NumberOfPoints 3 ; }
                    { GeoElement Line2 ; NumberOfPoints 4 ; } // Second-order element
                    { GeoElement Triangle ; NumberOfPoints 12 ; } // To ensure sufficent nb of points with hierarchical elements in coupled formulations (to be optimized)
                    { GeoElement Triangle2 ; NumberOfPoints 12 ; }
                    { GeoElement Quadrangle ; NumberOfPoints 4 ; }
                    { GeoElement Quadrangle2 ; NumberOfPoints 4 ; } // Second-order element
                      { GeoElement Tetrahedron ; NumberOfPoints  5 ; }
                    // { GeoElement Tetrahedron ; NumberOfPoints  15 ; }
                    { GeoElement Tetrahedron2 ; NumberOfPoints  5 ; } // Second-order element
                    { GeoElement Pyramid ; NumberOfPoints  8 ; }
                    { GeoElement Prism ; NumberOfPoints  9 ; }
                    { GeoElement Hexahedron ; NumberOfPoints  6 ; }
                }
            }
        }
    }
}


Constraint {
  { Name AGauge ;
    Case {
      { Region Omega; SubRegion BdOmega; Value 0. ; }
    }
  }
  { Name VoltageAV ;
    Case {
      {% for cut_name in rm.induced['cct'].cochain.names %}
	  { Region <<cut_name>>; Value 0. ; }
	  {% endfor %}
    }
  }
  { Name CurrentAV ;
    Case {
	  {% for cut_name, vol_name in zip(rm.powered['cct'].cochain.names, rm.powered['cct'].vol.names) %}
      { Region <<cut_name>>; Value I_<<vol_name>>[] ; }
	  {% endfor %}
    }
  }
}

FunctionSpace {
  { Name ASpace; Type Form1;
    BasisFunction {
      { Name se; NameOfCoef a; Function BF_Edge;
        Support <<nc.omega>>; Entity EdgesOf[All, Not <<nc.bd>><<nc.omega>>]; }
    }
    Constraint {
      { NameOfCoef a ;  // Gauge condition
	EntityType EdgesOfTreeIn ; EntitySubType StartingOn ;
	NameOfConstraint AGauge ; }
    }
  }
  { Name ESpace; Type Form1;
    BasisFunction {
      { Name sn; NameOfCoef v; Function BF_GradNode;
        Support <<nc.omega>><<nc.cond>>; Entity NodesOf[All, Not Terms]; }
      { Name sp; NameOfCoef V_p; Function BF_GroupOfEdges;
		Support <<nc.omega>><<nc.cond>>; Entity GroupsOfEdgesOf[Cuts<<nc.powered>>]; }
      { Name si; NameOfCoef V_i; Function BF_GroupOfEdges;
		Support <<nc.omega>><<nc.cond>>; Entity GroupsOfEdgesOf[Cuts<<nc.induced>>]; }
    }
    GlobalQuantity {
      { Name Voltage<<nc.powered>>    ; Type AliasOf        ; NameOfCoef V<<nc.powered>> ; }
      { Name Current<<nc.powered>>    ; Type AssociatedWith ; NameOfCoef V<<nc.powered>> ; }
      { Name Voltage<<nc.induced>>    ; Type AliasOf        ; NameOfCoef V<<nc.induced>> ; }
      { Name Current<<nc.induced>>    ; Type AssociatedWith ; NameOfCoef V<<nc.induced>> ; }
    }
    Constraint {
      { NameOfCoef Current<<nc.powered>> ;
        EntityType GroupsOfEdgesOf ; NameOfConstraint CurrentAV ; }
      { NameOfCoef Voltage<<nc.powered>> ;
        EntityType GroupsOfEdgesOf ; NameOfConstraint VoltageAV ; }
      { NameOfCoef Current<<nc.induced>> ;
        EntityType GroupsOfEdgesOf ; NameOfConstraint CurrentAV ; }
      { NameOfCoef Voltage<<nc.induced>> ;
        EntityType GroupsOfEdgesOf ; NameOfConstraint VoltageAV ; }
    }
  }
}
Formulation {
  { Name MagDynAV; Type FemEquation;
    Quantity {
      { Name a; Type Local; NameOfSpace ASpace; }
      { Name e; Type Local; NameOfSpace ESpace; }
      { Name I<<nc.powered>>; Type Global; NameOfSpace ESpace[Current<<nc.powered>>]; }
      { Name V<<nc.powered>>; Type Global; NameOfSpace ESpace[Voltage<<nc.powered>>]; }
      { Name I<<nc.induced>>; Type Global; NameOfSpace ESpace[Current<<nc.induced>>]; }
      { Name V<<nc.induced>>; Type Global; NameOfSpace ESpace[Voltage<<nc.induced>>]; }
    }
    Equation {
      Galerkin { [ 1./mu[] * Dof{d a} , {d a} ];
        In <<nc.omega>>; Integration Int; Jacobian Vol;  }
      Galerkin { [ sigma[] * Dof{e} , {a} ];
	In <<nc.omega>><<nc.cond>>; Integration Int; Jacobian Vol;  }
      Galerkin { DtDof [ sigma[] * Dof{a} , {a} ];
	In <<nc.omega>><<nc.cond>>; Integration Int; Jacobian Vol;  }
      Galerkin { [ sigma[] * Dof{e} , {e} ];
	In <<nc.omega>><<nc.cond>>; Integration Int; Jacobian Vol;  }
      Galerkin { DtDof [ sigma[] * Dof{a} , {e} ];
        In <<nc.omega>><<nc.cond>>; Integration Int; Jacobian Vol;  }
		GlobalTerm { [ - Dof{I<<nc.powered>>} , {V<<nc.powered>>} ] ; In Cuts<<nc.powered>>; }
		GlobalTerm { [ - Dof{I<<nc.induced>>} , {V<<nc.induced>>} ] ; In Cuts<<nc.induced>>; }
	{% for cut_name in rm.powered['cct'].cochain.names %}
	{% endfor %}
	{% for cut_name in rm.induced['cct'].cochain.names %}
	{% endfor %}
    }
  }
}
Resolution {
  { Name MagDynAVComplex;
    System {
      { Name A; NameOfFormulation MagDynAV; NameOfMesh mesh_file;}
    }
    Operation {
      Generate[A]; Solve[A]; SaveSolution[A];
    }
  }
}
PostProcessing {
  { Name MagDynAV; NameOfFormulation MagDynAV; 
    PostQuantity {
      { Name v; Value{ Local{ [ {dInv e} ] ;
	    In <<nc.omega>><<nc.cond>>; Jacobian Vol; } } }
      { Name e; Value{ Local{ [ -(Dt[ {a} ] + {e}) ] ;
	    In <<nc.omega>><<nc.cond>>; Jacobian Vol; } } }
      { Name a; Value{ Local{ [ {a} ] ;
	    In <<nc.omega>>; Jacobian Vol; } } }
      { Name b; Value{ Local{ [ {d a} ] ;
	    In <<nc.omega>>; Jacobian Vol; } } }
	  { Name b_norm; Value{ Local{ [Norm[ {d a} ]] ;
	    In <<nc.omega>>; Jacobian Vol; } } }
      { Name j; Value{ Local{ [  -sigma[]*(Dt[ {a} ] + {e}) ]  ;
          In <<nc.omega>><<nc.cond>>; Jacobian Vol; } } }
	  { Name j_norm; Value{ Local{ [ Norm[ -sigma[]*(Dt[ {a} ] + {e}) ]]  ;
          In <<nc.omega>><<nc.cond>>; Jacobian Vol; } } }
      { Name q; Value{ Local{ [  sigma[]* SquNorm[Dt[ {a} ] + {e}] ]  ;
          In <<nc.omega>><<nc.cond>>; Jacobian Vol; } } }
      { Name h; Value{ Local{ [ 1./mu[]*({d a}) ] ;
            In <<nc.omega>>; Jacobian Vol; } } }
	  {% for cut_name, vol_name in zip(rm.powered['cct'].cochain.names, rm.powered['cct'].vol.names) %}
      { Name I_<<vol_name>> ; Value { Term { [ {I_p} ] ; In <<cut_name>> ; } } }
      { Name V_<<vol_name>> ; Value { Term { [ {V_p} ] ; In <<cut_name>> ; } } }
      { Name Z_<<vol_name>> ; Value { Term { [ {V_p}/{I_p} ] ; In <<cut_name>> ; } } }
      { Name reI_<<vol_name>> ; Value { Term { [ Re[{I_p}] ] ; In <<cut_name>> ; } } }
      { Name reV_<<vol_name>> ; Value { Term { [ Re[{V_p}] ] ; In <<cut_name>> ; } } }
      { Name reZ_<<vol_name>> ; Value { Term { [ Re[{V_p}/{I_p}] ] ; In <<cut_name>> ; } } }
      { Name imI_<<vol_name>> ; Value { Term { [ Im[{I_p}] ] ; In <<cut_name>> ; } } }
      { Name imV_<<vol_name>> ; Value { Term { [ Im[{V_p}] ] ; In <<cut_name>> ; } } }
      { Name imZ_<<vol_name>> ; Value { Term { [ Im[{V_p}/{I_p}] ] ; In <<cut_name>> ; } } }
	  {% endfor %}
	  {% for cut_name, vol_name in zip(rm.induced['cct'].cochain.names, rm.induced['cct'].vol.names) %}
	    { Name I_<<vol_name>> ; Value { Term { [ {I_i} ] ; In <<cut_name>> ; } } }
      { Name V_<<vol_name>> ; Value { Term { [ {V_i} ] ; In <<cut_name>> ; } } }
      { Name reI_<<vol_name>> ; Value { Term { [ Re[{I_i}] ] ; In <<cut_name>> ; } } }
      { Name reV_<<vol_name>> ; Value { Term { [ Re[{V_i}] ] ; In <<cut_name>> ; } } }
      { Name imI_<<vol_name>> ; Value { Term { [ Im[{I_i}] ] ; In <<cut_name>> ; } } }
      { Name imV_<<vol_name>> ; Value { Term { [ Im[{V_i}] ] ; In <<cut_name>> ; } } }
	  {% endfor %}
    { Name MagEnergy ;  Value { Integral { [ 1/2 * nu[{d a}]*{d a} * {d a} ] ; In <<nc.omega>><<nc.cond>> ; Jacobian Vol ; Integration Int ; } } }
    { Name Inductance_from_MagEnergy ; Value { Term { Type Global; [ 2 * $MagEnergy /(I_<<rm.powered['cct'].vol.names[0]>>[]*I_<<rm.powered['cct'].vol.names[0]>>[]) ] ; In DomainDummy ; } } }  
    }
  }
}
 PostOperation {
  { Name Get_LocalFields ; NameOfPostProcessing MagDynAV ;
    Operation {
      //Print[ j, OnElementsOf Omega_p_1 , Format Table, File >> "J_Omega_p_1.txt"] ;
	  //Print [ b, OnLine { {0,0,-0.15} {0,0,0.15} } {125}, Format Table, File >> "line.txt" ];
	  //Print[ j, OnElementsOf Omega_p_1 , Format Gmsh, File "J_Omega_p_1_gmsh.pos"] ;
	  //Print[ j, OnElementsOf Omega_p_1 , Format GmshParsed, File "J_Omega_p_1_gmshparsed.pos"] ;
    //Print[ a, OnElementsOf <<nc.omega>><<nc.cond>> , File "a_<<nc.omega>><<nc.cond>>.pos"] ;
	  {% for var_name, vol_name, file_ext in zip(dm.solve.variables, dm.solve.volumes, dm.solve.file_exts) %}
	  Print[ <<var_name>>, OnElementsOf <<vol_name>> , File "<<var_name>>_<<vol_name>>.<<file_ext>>"] ;
	  {% endfor %}
	  Print [ b, OnLine {{0,0,<<dm.geometry.air.z_min>>}{0,0,<<dm.geometry.air.z_max>>}} {1000}, Format SimpleTable, File "Center_line.csv"];

	  //Print[ j, OnElementsOf Omega_p , File "j_Omega_p.pos"] ;
	  //Print[ j_norm, OnElementsOf Omega_p , File "j_norm_Omega_p.pos"] ;
	  //Print[ b_norm, OnElementsOf Omega_p , File "b_norm_Omega_p.pos"] ;
    Print[ MagEnergy[<<nc.omega>><<nc.cond>>], OnGlobal, Format TimeTable,
     File "Magnetic_energy.dat", StoreInVariable $MagEnergy,
     SendToServer "41Magnetic Energy [J]",  Color "LightYellow" ];
    Print [Inductance_from_MagEnergy, OnRegion DomainDummy, Format Table, File "Inductance.dat",
    SendToServer "51Inductance from Magnetic Energy [mH]", Color "LightYellow" ];
    }
  }
}