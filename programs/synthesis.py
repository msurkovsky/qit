import sys
sys.path.insert(0, "../src")

from qit import Qit, Map, Int, Mapping, System, Set, Struct, Product, Variable, Range, Join, Function, System, Vector, Values, Bool, Sequence, Class, KeyValue, ActionSystem

N_EVENTS           = 2
MAX_IN_ARC_WEIGHT  = 1
MAX_OUT_ARC_WEIGHT = 1
MAX_PLACE_MARKING  = 1

# Petri net definition
P = Range(N_EVENTS)
T = Range(N_EVENTS)
I = Product((P, "place"), (T, "transition"))
O = Product((T, "transition"), (P, "place"))

Wi = Mapping(I, Range(MAX_IN_ARC_WEIGHT + 1))  # weights of input arcs
Wo = Mapping(O, Range(MAX_OUT_ARC_WEIGHT + 1)) # weights of output arcs
M0 = Mapping(P, Range(MAX_PLACE_MARKING))      # mapping functions

################################################################################

ctx = Qit(debug=True)

v_mapping = M0.variable("mapping")
v_input_arcs = Wi.variable("input_arcs")
v_output_arcs = Wo.variable("output_arcs")

t_marking = M0.as_type()

fs_enabled = tuple(
     Function("t{}_is_enabled".format(t)).takes(t_marking, "mapping").reads(v_input_arcs).returns(Bool()).code("""
        for (auto it = input_arcs.begin(); it != input_arcs.end(); it++) {
            if (it->first.transition == {{_tid}} &&
                it->second > mapping.at(it->first.place)) {
                return false;
            }
        }
        return true;
     """, _tid=t)
     for t in range(N_EVENTS))

fs_fire = tuple(
    Function("t{}".format(t)).takes(t_marking, "mapping").reads(v_output_arcs).returns(Vector(t_marking)).code("""
        if ({{is_enabled}}(mapping)) {
            {{t_marking}} new_mapping(mapping);
            for (auto it = output_arcs.begin(); it != output_arcs.end(); it++) {
                if (it->first.transition == {{_tid}}) {
                    new_mapping[it->first.place] += it->second;
                }
            }
            return {new_mapping};
        }
        return {};
    """, is_enabled=fs_enabled[t], t_marking=t_marking, _tid=t)
    for t in range(N_EVENTS))

statespace = ActionSystem(Values(t_marking, [v_mapping]), fs_fire)
states = statespace.states(3)
f_states = states.iterate().make_function((v_mapping, v_input_arcs, v_output_arcs))

init_values = Product((M0, "init_marking"), (Wi, "input"), (Wo, "output"))

f_map_variables = Function("map_variables").takes(init_values, "init_values").returns(Vector(statespace.sas_type))
f_map_variables.code("""
    return {{f_states}}(init_values.init_marking, init_values.input, init_values.output);
""", f_states=f_states)


#t_states = Vector(t_extended_marking)
#f_eq_statespaces = Function("eq_statespaces").takes(t_states, "lts1").takes(t_states, "lts2").returns(Bool())
#f_eq_statespaces.code("""
        #if (lts1.size() != lts2.size()) {
            #return false;
        #}

        #std::sort(lts1.begin(), lts1.end(), {{cmp_emarkings}});
        #std::sort(lts2.begin(), lts2.end(), {{cmp_emarkings}});

        #for (int i = 0; i < lts1.size(); i++) {
            #if (!(eq_markings(lts1[i].marking, lts2[i].marking) &&
                    #lts1[i].transition == lts2[i].transition)) {
                #return false;
            #}
        #}
        #return true;
#""", cmp_emarkings=f_cmp_emarkings, eq_markings=f_eq_markings)

# TODO: affter filtering map a function which returns init_value
res = ctx.run(init_values.iterate().map(f_map_variables))

################################################################################

for r in res:
    print (r);
print ("total number: {}".format(len(res)))
print ("OK")
