import time
from dataclasses import dataclass

from src.instruments.base_option import BaseOption
from src.pipeline.pricing_pipeline import PricerName, PricingPipeline, PricingSettings
from src.pricers.monte_carlo import VarianceReductionTechnique
from src.process.base_process import StochasticProcess
from src.reporting.monte_carlo_accuracy.accuracy_result import MonteCarloAccuracyResult
from src.reporting.monte_carlo_accuracy.accuracy_run import AccuracyRun


@dataclass(frozen=True)
class MonteCarloAccuracyStudy:
    path_counts: tuple[int, ...] = (10_000, 50_000, 100_000)
    techniques: tuple[VarianceReductionTechnique, ...] = (
        VarianceReductionTechnique.NONE,
        VarianceReductionTechnique.ANTITHETIC,
        VarianceReductionTechnique.CONTROL_VARIATE,
    )

    def run(
        self,
        option: BaseOption,
        process: StochasticProcess,
        spot: float,
        settings: PricingSettings,
        reference_price: float,
    ) -> MonteCarloAccuracyResult:
        runs = [
            self._run(option, process, spot, settings, technique, paths)
            for technique in self.techniques
            for paths in self.path_counts
        ]
        return MonteCarloAccuracyResult(reference_price, settings.mc_confidence_level, runs)

    @staticmethod
    def _run(option, process, spot, settings: PricingSettings, technique: VarianceReductionTechnique, paths: int) -> AccuracyRun:
        run_settings = PricingSettings(
            mc_paths=paths,
            mc_steps=settings.mc_steps,
            mc_scheme=settings.mc_scheme,
            mc_variance_reduction=technique,
            mc_confidence_level=settings.mc_confidence_level,
            seed=settings.seed,
        )
        pricer = PricingPipeline.build_pricer(PricerName.MONTE_CARLO, run_settings)

        start = time.perf_counter()
        statistics = pricer.price_with_statistics(option, process, spot, confidence_level=settings.mc_confidence_level)
        return AccuracyRun(technique, paths, statistics, time.perf_counter() - start)
