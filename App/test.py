from sdv.single_table import GaussianCopulaSynthesizer, CTGANSynthesizer, CopulaGANSynthesizer, TVAESynthesizer
import pandas as pd
from sdv.metadata import SingleTableMetadata

real_data = pd.read_csv('./static/data/1_adult.csv')
metadata = SingleTableMetadata()
metadata.detect_from_dataframe(real_data)

#enable verbose mode

synthesizer = CTGANSynthesizer(metadata,verbose=True)
synthesizer.fit(real_data)
synthetic_data = synthesizer.sample(10)
print(synthetic_data)

