from opcua import Client

client = Client("opc.tcp://192.168.1.5:53530")



try:
    # Conecta ao servidor
    client.connect()
    print("✅ Conectado ao servidor OPC UA!")

    # Acessa o nó de objetos
    objects = client.get_objects_node()
    print("📦 Nó de objetos:", objects)

    # Procura pelo nó 'simulation'
    simulation = None
    for child in objects.get_children():
        name = child.get_browse_name().Name
        if name.lower() == "simulation":
            simulation = child
            break

    if simulation is None:
        print("Nó 'simulation' não encontrado.")
    else:
        print("Variáveis e valores em 'simulation':")
        for var in simulation.get_children():
            node_class = var.get_node_class()
            if node_class.name == "Variable":
                try:
                    value = var.get_value()
                    display_name = var.get_display_name().Text
                except Exception as e:
                    value = f"Erro ao ler valor: {e}"
                    display_name = "Erro ao obter displayName"
                print(f" - {display_name}: {value}")
            else:
                display_name = var.get_display_name().Text
                print(f" - {display_name}: {node_class.name}")

except Exception as e:
    print("Erro ao conectar ou acessar o servidor:", e)
    client.disconnect()

finally:
    # Encerra a conexão
    client.disconnect()
    print("🔌 Conexão encerrada.")