from typing import List

import pytest
from pymultirole_plugins.v1.schema import Document

from pysegmenters_pysdb.pysdb_segmenter import PySDBSegmenter, PySDBSegmenterParameters

from pysegmenters_syntok.syntok_segmenter import SyntokSegmenter, SyntokSegmenterParameters


def test_syntok_en():
    TEXT = """CLAIRSSON INTERNATIONAL REPORTS LOSS

Clairson International Corp. said it expects to report a net loss for its second quarter ended March 26.
The company doesn’t expect to meet analysts’ profit estimates of $3.9 to $4 million, or 76 cents a share to 79 cents a share, for its year ending Sept. 24, according to Pres. John Doe."""
    model = SyntokSegmenter.get_model()
    model_class = model.construct().__class__
    assert model_class == SyntokSegmenterParameters
    parameters = SyntokSegmenterParameters()
    segmenter = SyntokSegmenter()

    docs: List[Document] = segmenter.segment([Document(text=TEXT, metadata={'language':'en'})], parameters)
    doc0 = docs[0]
    assert len(doc0.sentences) == 4


def test_syntok_hi():
    TEXT = """यूएन महासभा में ईरानी राष्ट्रपति इब्राहिम रईसी का वार और चीन की अहम घोषणा ईरान के नए राष्ट्रपति इब्राहिम रईसी ने संयुक्त राष्ट्र महासभा के पहले संबोधन में अमेरिका को जमकर निशाने पर लिया है.
रईसी ने कहा कि ईरान पर प्रतिबंध को अमेरिका जंग की तरह इस्तेमाल कर रहा है. रईसी ने यूएन में अपने पूर्ववर्ती हसन रूहानी से भी ज़्यादा सख़्त रुख़ अपनाया.
रईसी ने पिछले महीने ही राष्ट्रपति पद की शपथ ली थी. इब्राहिम रईसी ईरान की सुप्रीम कोर्ट के पूर्व चीफ़ जस्टिस हैं और उन्हें रूढ़िवादी माना जाता है.
रईसी ने यूएन महासभा को तेहरान से वर्चुअली संबोधित किया. उन्होंने कहा, ''दुनिया के कई देशों के साथ अमेरिका प्रतिबंध को हथियार के तौर पर इस्तेमाल कर रहा है. कोविड महामारी के वक़्त में इस तरह की आर्थिक सज़ा मानवता के ख़िलाफ़ अपराध है.'' रईसी ने कहा, ''हमारे क्षेत्र अमेरिका न केवल अधिनायकवादी व्यवहार कर रहा है बल्कि पश्चिमी पहचान थोपने में लगा हुआ है. लेकिन उसे इसमें नाकामी ही हाथ लगी है. इराक़ और अफ़ग़ानिस्तान से अमेरिका ख़ुद गया नहीं बल्कि उसे वहाँ से निकाला गया है. अमेरिकी सैनिकों को अफ़ग़ानिस्तान से निकलना पड़ा और इराक़ से भी ऐसा ही करना पड़ रहा है.'' अमेरिका को निशाने पर लेते हुए रईसी ने इसी साल छह जनवरी को अमेरिका के कैपिटल हिल ट्रंप समर्थकों की हिंसा का भी हवाला दिया है. रईसी ने कहा, ''कैपिटल से काबुल तक स्पष्ट संदेश है कि अमेरिकी अधिनायकवादी सिस्टम की कोई साख है. वो चाहे अमेरिका के भीतर हो या बाहर.'' ईरान के राष्ट्रपति ने कहा, ''पश्चिमी तौर-तरीक़ों को थोपने की कोशिश नाकाम हो गई है. इराक़ और अफ़ग़ानिस्तान से ये साबित हो गया है. दुनिया को अमेरिकी नारों से कोई फ़र्क़ नहीं पड़ता है. वो चाहे ट्रंप का अमेरिका फर्स्ट हो या बाइडन का अमेरिका बैक.'' रईसी ने ईरान में 1979 की इस्लामिक क्रांति की तारीफ़ की और इसे धार्मिक लोकतंत्र से भी जोड़ा. उन्होंने पश्चिम में आतंकवाद में हुई बढ़ोतरी को अध्यात्म में आई गिरावट से भी जोड़ा. रईसी ने अपने संबोधन में कहा कि अमेरिका से बातचीत तभी शुरू हो सकती है जब कोई ठोस नतीजे की उम्मीद होगी और प्रतिबंध हटाए जाएंगे. उन्होंने कहा कि ईरान अमेरिकी सरकार के वादों पर भरोसा नहीं कर सकती है.
अमेरिकी अख़बार वॉशिंगटन पोस्ट के अनुसार, अमेरिकी विदेश मंत्रालय के एक अधिकारी ने कहा है कि उन्होंने रईसी के भाषण को सुना है लेकिन वे चाहते हैं कि ईरान अपने परमाणु कार्यक्रम पर कुछ ठोस करे.
रईसी ने कहा कि ईरान के रक्षा सिद्धांत में परमाणु हथियार और प्रतिरोधक नीति (डेटरेंस पॉलिसी) की कोई जगह नहीं है. अमेरिकी राष्ट्रपति जो बाइडन ने यूएन महासभा को संबोधित करते मंगलवार को कहा था कि अमेरिका अपने रुख़ पर कायम है कि वो ईरान को परमाणु हथियार हासिल नहीं करने देगा."""
    model = SyntokSegmenter.get_model()
    model_class = model.construct().__class__
    assert model_class == SyntokSegmenterParameters
    segmenter = SyntokSegmenter()
    parameters = SyntokSegmenterParameters()
    docs: List[Document] = segmenter.segment([Document(text=TEXT, metadata={'language':'hi'})], parameters)
    doc0 = docs[0]
    assert len(doc0.sentences) == 22


def test_syntok_fr():
    TEXT="""# PRESTATIONS DE SERVICE

Kairntech propose de migrer l'ensemble des composants Python de la plateforme vers la version 3.12 ou 3.13, mettre à jour les images Docker de base vers Ubuntu 22.04 ou 24.04 LTS, et garantir la traçabilité des binaires Python via un dépôt avec des backports de sécurité.

De manière détaillé, cela consiste en :

**Étape 1 : Évaluation et planification**

* Réalisation d’un audit complet de l'état actuel de la plateforme ;
* Liste exhaustive de tous les composants logiciels, micro-services et scripts qui utilisent Python ;
* Documentation des versions de Python actuellement déployées et les versions des images Docker de base utilisées ;
* Analyse de la matrice de dépendances pour comprendre l'impact de la migration de Python sur les bibliothèques clés, en particulier celles liées au NLP et à la GenAI (comme TensorFlow, PyTorch, Transformers, etc.), car elles peuvent avoir des prérequis de version spécifiques ;
* Disponibilité des paquets Python critiques dans les dépôts pour la version 3.12/3.13 afin d'anticiper les éventuels blocages ;
* Sélection du dépôt de paquets Python qui fournira les binaires avec des backports de sécurité.

**Étape 2 : Préparation de l'environnement de développement et des CI/CD**

* Mise à jour des fichiers de configuration des environnements de développement, tels que pyenv ou les Dockerfiles de développement, pour proposer la version Python 3.12/3.13 ;
* Modification des pipelines d'intégration continue (CI/CD) pour qu'ils créent des environnements de test parallèles utilisant Python 3.12/3.13 et Ubuntu 22.04/24.04 ;
* Configuration des pipelines pour qu'ils exécutent automatiquement les tests de non-régression et les analyses de sécurité de code à chaque commit sur la branche de migration.

**Étape 3 : Mise à jour des fichiers de dépendances et des images Docker**

* Mise à jour de tous les fichiers de définition des dépendances, comme requirements.txt ou pyproject.toml, en spécifiant les versions compatibles avec Python 3.12/3.13 ;
* Réécriture des Dockerfiles pour qu'ils utilisent l'image de base ubuntu 22.04/24.04 et qu'ils installent Python 3.12/3.13 exclusivement depuis le dépôt de backports de sécurité choisie ;
* Dans les Dockerfiles, documentation par un commentaire explicite l'URL source du dépôt utilisé pour l'installation de Python, afin de servir de preuve technique.

**Étape 4 : Adaptation du code et résolution des incompatibilités**

* Lancement de campagnes de tests et d'analyse statique du code avec des outils comme ruff ou bandit pour détecter les APIs devenues obsolètes ou les syntaxes non supportées ;
* Correction de toutes les incompatibilités identifiées, en accordant une attention particulière au code de bas niveau ou qui manipule les types de données de manière avancée ;
* Tests manuels approfondis sur les fonctionnalités les plus critiques de la plateforme pour valider le comportement attendu.

**Étape 5 : Validation intensive et recette**

* Exécution de la suite complète des tests automatisés, incluant les tests unitaires, d'intégration et de bout en bout, dans le nouvel environnement ;
* Réalisation des tests de charge et de performance pour assurer que la nouvelle stack n'introduit pas de dégradation.

**Étape 6 : Génération des preuves de conformité et de sécurité**

* Automatisation de la génération d'un rapport de conformité dans le pipeline CI/CD ;
* Ce rapport doit capturer la version exacte de Python installée et doit clairement indiquer l'origine du paquet, c'est-à-dire l'URL du dépôt de backports de sécurité."""
    segmenter = SyntokSegmenter()
    parameters = SyntokSegmenterParameters()
    docs: List[Document] = segmenter.segment([Document(text=TEXT, metadata={'language':'fr'})], parameters)
    doc0 = docs[0]
    assert len(doc0.sentences) == 25
