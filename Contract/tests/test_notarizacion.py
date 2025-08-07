import pytest
from brownie import Notarizacion, accounts

@ pytest.fixture
def contrato():
    return Notarizacion.deploy({'from': accounts[0]})


def test_notarizar_emite_evento(contrato):
    prueba_hash = b"\x12" * 32  # bytes32 ejemplo
    tx = contrato.notarizar(prueba_hash, {'from': accounts[0]})
    # Verificar que se haya emitido el evento con datos correctos
    assert len(tx.events) == 1
    event = tx.events['NotarizacionRealizada']
    assert event['autor'] == accounts[0]
    assert event['hashFoto'] == "0x" + prueba_hash.hex()
    assert contrato.registros(prueba_hash) > 0


def test_notarizar_unico(contrato):
    prueba_hash = b"\x34" * 32
    contrato.notarizar(prueba_hash, {'from': accounts[0]})
    timestamp_inicial = contrato.registros(prueba_hash)
    # Llamada segunda vez no debe volver a emitir ni alterar el registro
    tx2 = contrato.notarizar(prueba_hash, {'from': accounts[1]})
    assert len(tx2.events) == 0
    assert contrato.registros(prueba_hash) == timestamp_inicial
