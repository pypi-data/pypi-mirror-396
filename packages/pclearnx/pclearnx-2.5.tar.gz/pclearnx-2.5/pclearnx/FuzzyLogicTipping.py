import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt


def build_fuzzy_system():
    # Input variables
    quality = ctrl.Antecedent(np.arange(0, 11, 1), 'quality')
    service = ctrl.Antecedent(np.arange(0, 11, 1), 'service')

    # Output variable
    tip = ctrl.Consequent(np.arange(0, 26, 1), 'tip')

    # Input membership functions
    quality.automf(3, names=['poor', 'average', 'good'])
    service.automf(3, names=['poor', 'average', 'good'])

    # Output membership functions
    tip['low'] = fuzz.trimf(tip.universe, [0, 0, 13])
    tip['medium'] = fuzz.trimf(tip.universe, [0, 13, 25])
    tip['high'] = fuzz.trimf(tip.universe, [13, 25, 25])

    # Fuzzy rules
    rule1 = ctrl.Rule(quality['poor'] | service['poor'], tip['low'])
    rule2 = ctrl.Rule(service['average'], tip['medium'])
    rule3 = ctrl.Rule(service['good'] | quality['good'], tip['high'])

    # Control system
    system = ctrl.ControlSystem([rule1, rule2, rule3])
    return ctrl.ControlSystemSimulation(system), quality, service, tip


def main():
    tipping_sim, quality, service, tip = build_fuzzy_system()

    tipping_sim.input['quality'] = 6.5
    tipping_sim.input['service'] = 9.8
    tipping_sim.compute()

    print(f"Calculated tip: {tipping_sim.output['tip']:.2f}%")
    input("\nPress Enter to view plots...")

    plt.figure()
    quality.view()
    plt.title('Quality Membership Functions')

    plt.figure()
    service.view()
    plt.title('Service Membership Functions')

    plt.figure()
    tip.view(sim=tipping_sim)
    plt.title('Tip Output and Defuzzification')

    plt.show()


if __name__ == "__main__":
    main()
