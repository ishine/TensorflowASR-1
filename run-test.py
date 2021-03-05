from utils.user_config import UserConfig
from AMmodel.model import AM
from LMmodel.trm_lm import LM
import pypinyin

class ASR():
    def __init__(self, am_config, lm_config):

        self.am = AM(am_config)
        self.am.load_model(False)

        self.lm = LM(lm_config)
        self.lm.load_model(False)

    def decode_am_result(self, result):
        return self.am.decode_result(result)

    def stt(self, wav_path):

        am_result = self.am.predict(wav_path)
        if self.am.model_type == 'Transducer':
            am_result = self.decode_am_result(am_result[1:-1])
            lm_result = self.lm.predict(am_result)
            lm_result = self.lm.decode(lm_result[0].numpy(), self.lm.lm_featurizer)
        else:
            am_result = self.decode_am_result(am_result[0])
            lm_result = self.lm.predict(am_result)
            lm_result = self.lm.decode(lm_result[0].numpy(), self.lm.lm_featurizer)
        return am_result, lm_result

    def am_test(self, wav_path):
        # am_result is token id
        am_result = self.am.predict(wav_path)
        # token to vocab
        if self.am.model_type == 'Transducer':
            am_result = self.decode_am_result(am_result[1:-1])
        else:
            am_result = self.decode_am_result(am_result[0])
        return am_result


    def lm_test(self, txt):
        if self.lm.config['am_token']['for_multi_task']:
            pys = pypinyin.pinyin(txt, 8, neutral_tone_with_five=True)
            input_py = [i[0] for i in pys]

        else:
            pys = pypinyin.pinyin(txt)
            input_py = [i[0] for i in pys]

        # now lm_result is token id
        lm_result = self.lm.predict(input_py)
        # token to vocab
        lm_result = self.lm.decode(lm_result[0].numpy(), self.lm.lm_featurizer)
        return lm_result


if __name__ == '__main__':
    import time
    # USE CPU:
    # os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
    # USE one GPU:
    # os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    # limit cpu to 1 core:
    # import tensorflow as tf
    # tf.config.threading.set_inter_op_parallelism_threads(1)
    # tf.config.threading.set_intra_op_parallelism_threads(1)
    am_config = UserConfig(r'./conformerCTC(M)/am_data.yml', r'./conformerCTC(M)/conformerM.yml')
    lm_config = UserConfig(r'./transformer-logs/lm_data.yml', r'./transformer-logs/transformerO2OE.yml')
    asr = ASR(am_config, lm_config)

    # first inference will be slow,it is normal
    s=time.time()
    a, b = asr.stt(r'BAC009S0764W0121.wav')
    e=time.time()
    print(a)
    print(b)
    print('asr.stt first infenrence cost time:',e-s)

    # now it's OK
    s = time.time()
    a, b = asr.stt(r'BAC009S0764W0121.wav')
    e = time.time()
    print(a)
    print(b)
    print('asr.stt infenrence cost time:', e - s)
    s=time.time()
    print(asr.am_test(r'BAC009S0764W0121.wav'))
    e=time.time()
    print('asr.am_test cost time:',e-s)
    s=time.time()
    print(asr.lm_test('中介协会'))
    e=time.time()
    print('asr.lm_test cost time:',e-s)



