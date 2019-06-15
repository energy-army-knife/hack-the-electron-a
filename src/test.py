from src.data_loader import PowerDataLoader
import matplotlib.pyplot as plt

df_dataset = PowerDataLoader("../resources/load_pwr.csv").data_frame
print(df_dataset.index)
plt.plot(range(df_dataset.index.shape[0]), df_dataset.index.to_list())
plt.show()
