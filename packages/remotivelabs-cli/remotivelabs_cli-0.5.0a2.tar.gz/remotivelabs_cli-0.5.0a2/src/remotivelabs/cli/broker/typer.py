import typer

BrokerUrlOption = typer.Option("http://localhost:50051", is_eager=False, help="Broker URL", envvar="REMOTIVE_BROKER_URL")
ApiKeyOption = typer.Option(None, help="Cloud Broker API-KEY or access token", envvar="REMOTIVE_BROKER_API_KEY")
