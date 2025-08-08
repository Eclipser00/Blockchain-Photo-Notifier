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

## Guía de instalación y uso actualizada

Esta aplicación es un ejemplo educativo para notarizar fotos o vídeos mediante un contrato de Ethereum.  Las siguientes instrucciones reflejan la nueva estructura del repositorio y los cambios implementados:

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/Eclipser00/Blockchain-Photo-Notifier.git
   cd Blockchain-Photo-Notifier
   ```

2. **Instalar dependencias**

   Usa `pip` para instalar las bibliotecas necesarias:

   ```bash
   pip install -r requirements.txt
   ```

3. **Compilar y desplegar el contrato**

   El contrato `Notarizacion.sol` está en el directorio `Contract/contracts`.  Para compilarlo y desplegarlo necesitas [Brownie](https://eth-brownie.readthedocs.io/):

   ```bash
   cd Contract
   brownie compile
   # Lanza Ganache en segundo plano
   ganache-cli -p 7545 --blockTime 1 &
   # Despliega el contrato en la red local
   brownie run scripts/deploy.py --network development
   ```

   Apunta la dirección del contrato desplegado y la URL del nodo; los necesitarás en el siguiente paso.

4. **Configurar variables de entorno**

   Crea un archivo `.env` en la raíz del proyecto o exporta las siguientes variables en tu terminal:

   ```env
   ETH_NODE_URL=http://127.0.0.1:7545       # URL del nodo Ethereum (local o Infura)
   CONTRACT_ADDRESS=0x...                  # Dirección del contrato desplegado
   CHAIN_ID=1337                           # ID de la red (1337 para Ganache, 1 para mainnet)
   GAS_LIMIT=100000                        # Límite de gas para las transacciones
   GAS_PRICE_GWEI=1.0                      # Precio del gas en Gwei
   NOTARIZACION_KEY_PASSWORD=tu_clave      # Contraseña opcional para cifrar la clave privada
   ```

5. **Ejecutar la aplicación**

   Desde la raíz del proyecto ejecuta:

   ```bash
   python main.py
   ```

   - **En Android**: compila la app con [Buildozer](https://buildozer.readthedocs.io/) u otra herramienta.  La aplicación solicitará permisos de cámara y almacenamiento, capturará la foto con la aplicación nativa y registrará el hash en la blockchain.
   - **En Windows/Linux/macOS**: la aplicación abre la webcam usando OpenCV; al hacer clic se captura la imagen, se generan los metadatos y se registra en la blockchain.

Estas instrucciones sustituyen a la guía anterior.
