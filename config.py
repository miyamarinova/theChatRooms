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