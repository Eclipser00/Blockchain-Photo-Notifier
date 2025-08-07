# Notarización de Fotos en Blockchain

Una aplicación móvil para capturar fotos/vídeos, generar un hash con metadatos y registrarlo en Ethereum como prueba de autoría e integridad.

## Características

- Captura in-app o nativa según permisos.
- Extracción automática de EXIF, sensores y ID de dispositivo.
- Generación de hash SHA-256 y firma digital.
- Interacción con Ethereum vía Web3.py.
- Notarización on-chain y verificación pública.

## Requisitos previos

- Python 3.9
- pip

## Instalación

1. Clonar el repositorio(aun no existe):
   ```bash
   git clone https://github.com/usuario/proyecto_notarizacion.git
   cd proyecto_notarizacion
   
2. Instalar dependencias:

       pip install -r requirements.txt

3. Generar el contrato:

Compilar


    brownie compile
    



buscar archivo build/contracts/Notarizacion.json, renombrar a contract_abi.json 

y pegar en directorio raiz.

4. Arrancar ganache en terminal limpia


    ganache-cli -p 7545 --blockTime 1

5. Arrancar brownie


    cd Contract
    brownie run scripts/deploy.py --network development


6. Configuración

Copiar .env.example a .env y configurar:
         
ETH_NODE_URL=https://mainnet.infura.io/v3/TU_PROYECTO_INFURA

CONTRACT_ADDRESS=0xTuContratoEthereum
    
CHAIN_ID=1

KEY_ALIAS=notarizacion_alias

GAS_LIMIT=100000

GAS_PRICE_GWEI=1.0

4.Uso 
    python main.py
