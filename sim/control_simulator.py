import numpy as np
import matplotlib.pyplot as plt

class SiennaControlSimulator:
    def __init__(self, scale_pos=7692, scale_neg=2589, slew_limit=820):
        """
        Sienna 2024 Control Simulator
        - Neutral point: 289
        - Range: [-2300, 7981]
        - scale_pos: distance from neutral to 7981 (7981 - 289 = 7692)
        - scale_neg: distance from neutral to -2300 (289 - (-2300) = 2589)
        """
        self.NEUTRAL = 289
        self.LIMIT_NEG = -2300
        self.LIMIT_POS = 7981
        self.SCALE_POS = scale_pos
        self.SCALE_NEG = scale_neg
        self.SLEW_LIMIT = slew_limit
        
        self.current_setpoint = self.NEUTRAL

    def map_request(self, req_slew):
        """
        Maps openpilot request [-1, 1] to Sienna setpoint range.
        req_slew > 0 -> Positive Range [289, 7981]
        req_slew < 0 -> Negative Range [-2300, 289]
        """
        if req_slew >= 0:
            val = self.NEUTRAL + (req_slew * self.SCALE_POS)
            return np.clip(val, self.NEUTRAL, self.LIMIT_POS)
        else:
            # req_slew is negative, so we add it to neutral (decreasing the value)
            val = self.NEUTRAL + (req_slew * self.SCALE_NEG)
            return np.clip(val, self.LIMIT_NEG, self.NEUTRAL)

    def apply_slew_rate(self, target_setpoint):
        """
        Applies the slew rate limit to prevent ACU safety trips.
        """
        diff = target_setpoint - self.current_setpoint
        if abs(diff) > self.SLEW_LIMIT:
            # Limit change to SLEW_LIMIT in either direction
            self.current_setpoint += np.sign(diff) * self.SLEW_LIMIT
        else:
            self.current_setpoint = target_setpoint
        return self.current_setpoint

def run_simulation():
    sim = SiennaControlSimulator()
    
    # Test Cases: 
    # 1. Gradual ramp up to max positive
    # 2. Sudden jump to max negative (Slew test)
    # 3. Recovery back to neutral
    
    time_steps = 200
    requests = np.zeros(time_steps)
    
    # Ramp Up [0, 50]
    for i in range(0, 50): requests[i] = i / 50.0
    # Hold Max [50, 80]
    for i in range(50, 80): requests[i] = 1.0
    # Sudden Jump to -1 [80, 81]
    requests[80] = -1.0
    # Hold Min [81, 130]
    for i in range(81, 130): requests[i] = -1.0
    # Ramp back to neutral [130, 180]
    for i in range(130, 180): requests[i] = (i-130)/50.0 * -1.0 # wait, let's just ramp from -1 to 0
    for i in range(130, 180): requests[i] = -1.0 + (i-130)/50.0

    mapped_vals = []
    slew_vals = []
    
    for req in requests:
        target = sim.map_request(req)
        actual = sim.apply_slew_rate(target)
        mapped_vals.append(target)
        slew_vals.append(actual)

    plt.figure(figsize=(12, 6))
    plt.plot(requests, label='Openpilot Request [-1, 1]', color='blue', alpha=0.5)
    plt.plot(np.array(mapped_vals)/8000, label='Mapped Setpoint (Normalized)', color='green', linestyle='--')
    plt.plot(np.array(slew_vals)/8000, label='Slew Limited Output (Normalized)', color='red', linewidth=2)
    plt.axhline(y=289/8000, color='black', linestyle=':', label='Neutral')
    plt.title("Toyota Sienna 2024 Control Simulation")
    plt.xlabel("Time Step")
    plt.ylabel("Normalized Value (Value / 8000)")
    plt.legend()
    plt.grid(True)
    plt.savefig("/home/vance/ToyotaSienna2024OpenpilotAnalysis/sim/simulation_result.png")
    
    # Also print some critical boundary points
    print(f"Neutral: {sim.map_request(0)}")
    print(f"Max Pos: {sim.map_request(1)}")
    print(f"Max Neg: {sim.map_request(-1)}")

if __name__ == "__main__":
    run_simulation()
