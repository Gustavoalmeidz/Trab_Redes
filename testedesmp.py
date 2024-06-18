import matplotlib.pyplot as plt

# Dados
protocols = ['TCP', 'UDP', 'UDPMod']
total_time = [2.5, 0.2, 4.0]
average_time = [0.02, 0.0002, 0.004]
colors_total = ['tab:blue', 'tab:red', 'tab:orange']
colors_average = ['tab:blue', 'tab:red', 'tab:orange']

# Configuração do gráfico
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# Plotando Tempo Total
axes[0].bar(protocols, total_time, color=colors_total, alpha=1.0)
axes[0].set_title('Tempo Total por Protocolo')
axes[0].set_ylabel('Tempo (segundos)')

# Plotando Tempo Médio
axes[1].bar(protocols, average_time, color=colors_average, alpha=1.0)
axes[1].set_title('Tempo Médio por Protocolo')

# Ajustando o layout
plt.tight_layout()
plt.show()
