// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Notarizacion {
    // Evento que se dispara al registrar un hash
    event NotarizacionRealizada(
        address indexed autor,
        bytes32 indexed hashFoto,
        uint256 timestamp
    );

    // Mapeo para guardar primer timestamp de cada hash
    mapping(bytes32 => uint256) public registros;

    /**
     * @dev Registra el hash de una foto/vídeo en la blockchain.
     *      Si el hash ya existe, no vuelve a emitir el evento.
     * @param hashFoto El hash de la foto/vídeo (SHA-256)
     */
    function notarizar(bytes32 hashFoto) external {
        require(hashFoto != bytes32(0), "Hash no puede ser cero");

        // Si es la primera vez, guardamos el timestamp y emitimos evento
        if (registros[hashFoto] == 0) {
            registros[hashFoto] = block.timestamp;
            emit NotarizacionRealizada(msg.sender, hashFoto, block.timestamp);
        }
    }
}