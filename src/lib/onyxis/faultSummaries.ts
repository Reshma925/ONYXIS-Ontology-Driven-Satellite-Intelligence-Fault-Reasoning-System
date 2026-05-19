const SUMMARY_MAP: Record<string, string> = {
  S1: "Zero charge rate in BatteryChargeController",
  S2: "Sensor failure warning generation",
  S3: "Critical battery overheating above 60°C",
  S4: "Battery overheating above 50°C",
  S5: "Dependency-based reduced performance",
  S6: "Combined solar and battery power failure",
  S7: "Communication degradation from TTC faults",
  S8: "Low regulator voltage condition",
  S9: "Vibration anomaly warning",
  S10: "Zero upconverter carrier frequency",
  S11: "Heater activation during underheat",
  S12: "Low tracking accuracy condition",
  S13: "Excessive battery discharge rate",
  S14: "Zero thruster output",
  S15: "Low temperature sensor accuracy",
  S16: "Invalid telemetry encoding quality",
  S17: "Low TTCRadio transmit power",
  S18: "Weak TTC antenna signal",
  S19: "High SunSensor vector error",
  S20: "Structural failure propagation through supports",
  S21: "SafeMode during structural failure",
  S22: "High StarTracker tracking error",
  S23: "Severe solar panel degradation",
  S24: "Excessive battery cycle usage",
  S25: "Low solar irradiance condition",
  S26: "Low solar power generation",
  S27: "Generic sensor fault warning",
  S28: "Excessive reaction wheel vibration",
  S29: "Low spacecraft bus voltage",
  S30: "Low power amplifier output",
  S31: "Low PCDU output voltage",
  S32: "Poor PCDU load balancing",
  S33: "Excessive PCDU distribution load",
  S34: "SafeMode during overheating",
  S35: "Critically low battery charge",
  S36: "Excessive orbital deviation",
  S37: "Zero magnetorquer magnetic moment",
  S38: "Magnetometer measurement anomaly",
  S39: "Low oscillator frequency stability",
  S40: "Low LNA gain condition",
  S41: "Heater output failure",
  S42: "Excessive gyroscope angular rate",
  S43: "Poor ground communication link quality",
  S44: "High GNSS position error",
  S45: "Low filter bandwidth condition",
  S46: "Excessive attitude control error",
  S47: "HIGH severity operational response",
  S48: "MEDIUM severity operational response",
  S49: "LOW severity operational response",
  S50: "Zero encoder transmission rate",
  S51: "High EarthSensor vector error",
  S52: "Poor duplexer isolation",
  S53: "Invalid downconverter frequency shift",
  S54: "Deployment anomaly warning",
  S55: "High demodulator bit error rate",
  S56: "Excessive decoder error rate",
  S57: "Battery underheating below 0°C",
  S58: "Excessive TTC antenna pointing error",
  S59: "Excessive antenna pointing error",
  S60: "RF subsystem overheating",
  S61: "PCDU overheating condition",
  S62: "OBC overheating condition",
  S63: "Weak command receiver signal",
  S64: "Weak antenna signal condition",
};

function cleanName(name?: string) {
  if (!name) return "";
  return name
    .replace(/_+/g, " ")
    .replace(/FaultState|Fault|FailureState|Failure/gi, "")
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .trim();
}

function extractSCode(rule?: string) {
  if (!rule) return null;
  const trimmed = rule.trim().toUpperCase();
  const sMatch = trimmed.match(/\bS0*([1-9][0-9]?)\b/);
  if (sMatch) return `S${Number(sMatch[1])}`;
  const rMatch = trimmed.match(/\bR0*([1-9][0-9]?)\b/);
  if (rMatch) return `S${Number(rMatch[1])}`;
  const ruleMatch = trimmed.match(/\b(?:SWRL\s*)?RULE\s*0*([1-9][0-9]?)\b/);
  if (ruleMatch) return `S${Number(ruleMatch[1])}`;
  return null;
}

export function getRuleLabel(rule?: string, faultName?: string) {
  const trimmed = rule?.trim();
  if (trimmed && trimmed !== "UNKNOWN" && trimmed !== "NONE" && trimmed !== "CLASS_INFERENCE") {
    const code = extractSCode(trimmed) || trimmed;
    return code;
  }
  return cleanName(faultName) || (faultName ?? "");
}

export function getFaultSummary(rule?: string, faultName?: string) {
  const code = extractSCode(rule);
  if (code && SUMMARY_MAP[code]) return SUMMARY_MAP[code];
  const cleaned = cleanName(faultName);
  return cleaned || (faultName ?? "");
}

export default SUMMARY_MAP;
