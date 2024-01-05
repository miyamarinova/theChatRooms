class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    SECRET_KEY = 'alabalanica123456'
    OPENAI_KEY = "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"
    
config = {
    'development': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'production': DevelopmentConfig
}