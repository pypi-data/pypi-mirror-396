import logging
from abc import abstractmethod
from getfactormodels.http_client import HttpClient

class FactorModel(ABC):
    def __init__(self, frequency: str = 'm',
            start_date: Optional[str] = None,
            end_date: Optional[str] = None,
            output_file: Optional[str] = None,
            cache_ttl = 86400
        ) -> None:
        
        self.frequency = frequency.lower()
        self.start_date = start_date
        self.end_date = end_date
        self.output_file = output_file

        self._validate_freq()

        logger.info(f"Initialized {self.__class__.__name__} with {self.frequency} frequency")

    def _validate_freq(self) -> None:
        """Validates common params between models."""
        if not hasattr(self, 'FREQUENCIES'):
            raise NotImplementedError("Subclass has not defined FREQUENCIES")
        
        if self.frequency not in self._FREQUENCIES:
            raise ValueError(
                f"Invalid frequency '{self.frequency}'. "
                f"Must be one of: {', '.join(sorted(self._FREQUENCIES))}"
            )
    def _download(self, url: str):
        """Download model from url."""
        logger.debug(f"Downloading from {url}")
        with HttpClient(timeout=15.0) as client:
            return client.download(url, cache_ttl)

    def download(self):
        # Will be public get_factors (will use _download, do this etc.),
        #  removed from here soon.
        raise NotImplementedError("download not impl")

    @property
    def url(self):
        ...
    @abstractmethod
    def _build_url(self) -> str:
        """Construct a url for a specific model/freq."""
        raise NotImplementedError("_build_url not implemented by model")

    #@abstractmethod
    #def _validate_model(self) -> None:
    #    """Model specific validation."""
    #    pass

    #@abstractmethod
    #def _get_url(self) -> str:
    #    """Constructs url for download. Model, freq. Returns url as str."""
    #    ...
