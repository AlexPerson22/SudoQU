from sqlalchemy import create_engine, Column, String, Integer, Date, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Creation of the base class for our data models
Base = declarative_base()


class Documents(Base):
    __tablename__ = 'documents'

    # Definition of table columns
    ID = Column(String(25), primary_key=True)
    NUMERO_PROJET = Column(String(20))
    NUMERO_COMMANDE = Column(BigInteger)
    LIGNE = Column(Integer)
    RELEASE = Column(String(5))
    FOURNISSEUR = Column(String(100))
    DATE_RECEPTION_MATERIEL = Column(Date)
    DATE_OBTENTION_DOC = Column(Date)
    DESCRIPTION = Column(String(150))
    ITEM_CODE = Column(String(30))
    STATUT = Column(String(50))
    COMMENTAIRES = Column(String(100))
    CONSULTANT = Column(String(30))
    ORIGINE_DOC = Column(String(10))
    HOROD_CONTROLE_VALIDE_SYSTEME = Column(Date)
    HOROD_CONTROLE_VALIDE_CELLULE_DOC = Column(Date)
    HOROD_ATTENTE_RETOUR_FOURNISSEUR = Column(Date)
    HOROD_ATTENTE_DOC = Column(Date)
    HOROD_ATTENTE_RETOUR_INTERNE = Column(Date)
    HOROD_LIGNE_INVALIDABLE = Column(Date)


# Database connection configuration
engine = create_engine('postgresql+psycopg://user_connection:thermodyn@localhost:5432/cellule_doc?')
# Creation of tables in the database if they don't already exist
Base.metadata.create_all(engine)

# Creation of a session to enable transactions with the database
Session = sessionmaker(bind=engine)
