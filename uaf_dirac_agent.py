import numpy as np


EPS = 1e-9


class UAFDiracAgent:
    """
    Online anomaly detector without training.

    UAF translation of a 2-component Dirac dynamics:
    - mass / beta term: crystallized past, the regime's structural inertia
    - momentum / alpha term: present flow pressure
    - phase curvature: local reorientation of the regime
    - spinor polarization: whether structure or motion dominates
    - event score: mass-gap breach, inversion, and zitter energy jump
    """

    def __init__(
        self,
        norm_window=50,
        short_window=20,
        long_window=60,
        baseline_window=120,
        dt=0.060,
        ema=0.10,
        threshold_k=3.0,
        min_gap=30,
        gap_weight=0.25,
        inversion_weight=0.35,
        zitter_weight=0.40,
        squash_scale=3.0,
    ):
        self.norm_window = norm_window
        self.short_window = short_window
        self.long_window = long_window
        self.baseline_window = baseline_window
        self.dt = dt
        self.ema = ema
        self.threshold_k = threshold_k
        self.min_gap = min_gap
        self.gap_weight = gap_weight
        self.inversion_weight = inversion_weight
        self.zitter_weight = zitter_weight
        self.squash_scale = squash_scale
        self.reset()

    def reset(self):
        self.values = []
        self.raw_scores = []
        self.a = 1.0 + 0.0j
        self.b = 0.0 + 0.0j
        self.prev_energy = 0.0
        self.smooth_score = 0.0
        self.last_event_index = -10**9

    @staticmethod
    def _gamma_balance(segment):
        segment = np.asarray(segment, dtype=np.float64)
        if len(segment) < 5:
            return 0.5
        diffs = np.diff(segment)
        sigma = np.std(segment)
        if sigma < EPS:
            return 0.5
        entropy = np.mean(np.abs(diffs)) / sigma
        chaos = np.var(segment)
        return float(np.clip(entropy / (entropy + chaos + EPS), 0.0, 1.0))

    def _normalize_current(self):
        end = len(self.values)
        start = max(0, end - self.norm_window)
        chunk = np.asarray(self.values[start:end], dtype=np.float64)
        sigma = np.std(chunk)
        if sigma < EPS:
            sigma = EPS
        return float((self.values[-1] - np.mean(chunk)) / sigma)

    def _normalized_history(self):
        normed = []
        for i in range(len(self.values)):
            start = max(0, i + 1 - self.norm_window)
            chunk = np.asarray(self.values[start:i + 1], dtype=np.float64)
            sigma = np.std(chunk)
            if sigma < EPS:
                sigma = EPS
            normed.append(float((self.values[i] - np.mean(chunk)) / sigma))
        return np.asarray(normed, dtype=np.float64)

    def _step_raw_score(self, signal):
        i = len(signal) - 1
        if i < self.long_window:
            return 0.0, {}

        short = signal[i - self.short_window:i]
        long = signal[i - self.long_window:i]

        gamma_short = self._gamma_balance(short)
        gamma_long = self._gamma_balance(long)
        gamma_collapse = max(0.0, gamma_long - gamma_short)

        d_short = np.diff(short)
        d_long = np.diff(long)
        pressure_short = np.std(d_short) + np.mean(np.abs(d_short))
        pressure_long = np.std(d_long) + np.mean(np.abs(d_long)) + EPS
        momentum = max(0.0, pressure_short / pressure_long - 1.0)
        curvature = abs(signal[i] - 2.0 * signal[i - 1] + signal[i - 2])

        # UAF Dirac Hamiltonian:
        # H = p*sigma_x + curvature*sigma_y + mass*sigma_z
        # mass is stabilized past; p is present pressure.
        mass = 0.15 + 0.85 * gamma_short
        hx = momentum + 0.35 * gamma_collapse
        hy = 0.35 * curvature
        hz = mass

        ha = hz * self.a + (hx - 1j * hy) * self.b
        hb = (hx + 1j * hy) * self.a - hz * self.b

        self.a -= 1j * self.dt * ha
        self.b -= 1j * self.dt * hb

        norm = np.sqrt(abs(self.a) ** 2 + abs(self.b) ** 2)
        if norm < EPS:
            self.a = 1.0 + 0.0j
            self.b = 0.0 + 0.0j
            norm = 1.0
        self.a /= norm
        self.b /= norm

        ab = np.conj(self.a) * self.b
        polarization = abs(self.a) ** 2 - abs(self.b) ** 2
        mix = 2.0 * ab.real
        phase = 2.0 * ab.imag
        energy = hx * mix + hy * phase + hz * polarization

        gap_breach = max(0.0, np.sqrt(hx * hx + hy * hy) / (hz + EPS) - 1.0)
        inversion = max(0.0, -polarization)
        zitter = abs(energy - self.prev_energy)
        self.prev_energy = energy

        score = (
            self.gap_weight * gap_breach
            + self.inversion_weight * inversion
            + self.zitter_weight * zitter
        )
        self.smooth_score = self.ema * score + (1.0 - self.ema) * self.smooth_score

        state = {
            "gamma_short": gamma_short,
            "gamma_long": gamma_long,
            "mass": mass,
            "momentum": momentum,
            "curvature": curvature,
            "polarization": float(polarization),
            "gap_breach": float(gap_breach),
            "inversion": float(inversion),
            "zitter": float(zitter),
            "energy": float(energy),
        }
        return self.smooth_score, state

    def update(self, timestamp, value):
        self.values.append(float(value))
        signal = self._normalized_history()
        raw_score, state = self._step_raw_score(signal)
        self.raw_scores.append(raw_score)

        i = len(self.raw_scores) - 1
        if i < self.baseline_window:
            return None

        hist = np.asarray(self.raw_scores[i - self.baseline_window:i], dtype=np.float64)
        sigma = np.std(hist)
        if sigma < EPS:
            sigma = EPS
        z = (raw_score - np.mean(hist)) / sigma

        if z <= self.threshold_k or i - self.last_event_index <= self.min_gap:
            return None

        self.last_event_index = i
        event_score = 1.0 - np.exp(-z / self.squash_scale)
        return {
            "timestamp": timestamp,
            "index": i,
            "score": float(event_score),
            "raw_score": float(raw_score),
            "z": float(z),
            "reason": "UAF-Dirac mass-gap breach / inversion / zitter jump",
            **state,
        }

    def score_sequence(self, values):
        self.reset()
        scores = np.zeros(len(values), dtype=np.float64)
        for i, value in enumerate(values):
            event = self.update(i, value)
            if event is not None:
                scores[i] = event["score"]
        return scores
