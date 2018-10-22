TEMPLATE = app
CONFIG += console c++11
CONFIG -= app_bundle
CONFIG -= qt

SOURCES += main.cpp \
    winsocket.cpp

HEADERS += \
    winsocket.h \
    helpers.h \
    conf.h
LIBS += -lWs2_32
