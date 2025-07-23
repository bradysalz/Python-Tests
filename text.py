import streamlit as st

def make_body():

    st.markdown("The time required to synthesize a target concentration of HOCl via electrolysis can be calculated using a modified form of Faraday's laws of electrolysis.")

    st.markdown("The primary reaction for chlorine generation at the anode from a sodium chloride (NaCl) solution is:")

    st.latex("2Cl^- \rightarrow Cl_2 + 2e^-")

    st.markdown("The chlorine then reacts with water to form HOCl:")

    st.latex("Cl_2 + H_2O \rightleftharpoons HOCl + HCl")

    st.markdown("Assuming 1 mole of Cl_2 produces 1 mole of HOCl, and 2 electrons are required per mole of Cl_2, the number of electrons (`z`) transferred per mole of HOCl produced is 2.")

    st.markdown("The formula is:")

    st.latex("t=\frac{ppm_{target} \times V_{container} \times z \times F}{1000 \times I \times M_{HOCl} \times \eta}")

    st.markdown("Where:")

    st.markdown("""
    - $t$: Time required (seconds)
    - $ppm_{target}$: Desired HOCl concentration (parts per million, equivalent to mg of HOCl per liter of solution)
    - $V_{container}$: Volume of the solution in the container (Liters)
    - $z$: Number of electrons transferred per mole of HOCl. For HOCl synthesis from Cl_2, $z=2$.
    - $F$: Faraday's constant (96485 C/mol or 96485 A⋅s/mol)
    - $I$: Applied current (Amperes, A)
    - $M_{HOCl}$: Molar mass of HOCl (approximately 52.46 g/mol)
    - $\eta$: Faradaic efficiency (a dimensionless value between 0 and 1, representing the fraction of current that actually contributes to HOCl production; typically ranges from 0.2 in low quality setups, to averaging 0.5 with membrane based setups, to peaking around 0.8 to 0.90 for well-designed industrial systems).
    """)
