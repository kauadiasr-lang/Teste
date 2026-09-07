import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ser_consciente.corpo import EstadoInterno
from ser_consciente.memoria import MemoriaAssociativa
from ser_consciente.persistencia import carregar, salvar
from ser_consciente.ser import Ser


class TestMemoriaAssociativa(unittest.TestCase):
    def test_reforca_conceitos_repetidos(self):
        m = MemoriaAssociativa()
        m.perceber("gato gosta de dormir")
        m.perceber("gato gosta de comer")
        self.assertGreaterEqual(m.conceitos["gato"].peso, 2.0)
        self.assertIn("gosta", m.conceitos["gato"].conexoes)

    def test_decaimento_reduz_peso_com_o_tempo(self):
        m = MemoriaAssociativa(taxa_decaimento=0.5)
        m.perceber("floresta")
        peso_inicial = m.conceitos["floresta"].peso
        m.decair()
        self.assertLess(m.conceitos["floresta"].peso, peso_inicial)

    def test_esquecimento_remove_conceitos_muito_fracos(self):
        m = MemoriaAssociativa(taxa_decaimento=0.9)
        m.perceber("eco")
        for _ in range(20):
            m.decair()
        self.assertNotIn("eco", m.conceitos)


class TestEstadoInterno(unittest.TestCase):
    def test_descanso_recupera_energia_com_o_tempo_real(self):
        estado = EstadoInterno(energia=10.0)
        estado.ultima_atualizacao = time.time() - 100  # 100s de ausência simulada
        estado.tick()
        # recupera 100s * 0.2/s = 20, menos o custo metabólico fixo de 0.5
        self.assertAlmostEqual(estado.energia, 29.5, places=3)

    def test_tick_sem_ausencia_nao_recupera_energia(self):
        estado = EstadoInterno(energia=10.0)
        estado.tick()
        self.assertLess(estado.energia, 10.0)


class TestSer(unittest.TestCase):
    def test_responde_e_gera_pensamento(self):
        ser = Ser()
        resposta = ser.responder("o mar é imenso e azul")
        self.assertIsInstance(resposta, str)
        self.assertGreater(len(resposta), 0)
        self.assertEqual(ser.identidade.numero_interacoes, 1)

    def test_pensamentos_realimentam_a_memoria(self):
        ser = Ser()
        ser.responder("montanha e rio e vento")
        self.assertGreater(len(ser.memoria.conceitos), 0)
        self.assertGreater(len(ser.monologo), 0)

    def test_estado_atual_nao_quebra_sem_memoria(self):
        ser = Ser()
        texto = ser.estado_atual()
        self.assertIn("Idade", texto)


class TestPersistencia(unittest.TestCase):
    def test_mantem_memoria_e_identidade_entre_sessoes(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = os.path.join(tmp, "ser.json")
            ser = Ser()
            ser.responder("estrelas brilham na noite escura")
            nome_original = ser.identidade.nome
            salvar(ser, caminho)

            ser2 = carregar(caminho)
            self.assertEqual(ser2.identidade.nome, nome_original)
            self.assertEqual(ser2.identidade.numero_interacoes, 1)
            self.assertIn("estrelas", ser2.memoria.conceitos)

    def test_carregar_sem_arquivo_cria_ser_novo(self):
        with tempfile.TemporaryDirectory() as tmp:
            caminho = os.path.join(tmp, "nao_existe.json")
            ser = carregar(caminho)
            self.assertEqual(ser.identidade.numero_interacoes, 0)


if __name__ == "__main__":
    unittest.main()
