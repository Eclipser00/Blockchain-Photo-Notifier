from brownie import Notarizacion, accounts, network

def main():
    # Seleccionar cuenta por defecto o por alias
    #acct = accounts.load('default') descomentar cuando use infura.
    acct = accounts[0]
    print(f"Desplegando desde: {acct.address}")

    # Desplegar contrato
    contrato = Notarizacion.deploy({'from': acct})

    print(f"Contrato desplegado en: {contrato.address}")
    return contrato