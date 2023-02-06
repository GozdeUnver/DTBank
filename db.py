from app import institutes
import MySQLdb

# To run the following script, you need to have an active MySQL server running locally. 
 # Enter your password and database name for the last two parameters, respectively


con = MySQLdb.connect('localhost', 'root', 'group4','dtbank')
cur = con.cursor()
# Following code creates the refined tables

cur.execute("CREATE TABLE User( \
    name VARCHAR(30), \
    username VARCHAR(30), \
    institute VARCHAR(100), \
    password CHAR(64), \
    PRIMARY KEY(username,institute))")

cur.execute("CREATE TABLE DatabaseManager(\
    username VARCHAR(30), \
    password VARCHAR(64), \
    PRIMARY KEY(username))")

cur.execute("CREATE TABLE UniProt( \
    uniprot_id CHAR(6), \
    sequence TEXT, \
    PRIMARY KEY(uniprot_id))")

cur.execute("CREATE TABLE Drug( \
    drugbank_id CHAR(7), \
    name VARCHAR(30), \
    description TEXT, \
    smiles VARCHAR(200), \
    PRIMARY KEY(drugbank_id), \
    UNIQUE(name))")


cur.execute("CREATE TABLE Interacts ( \
    interactor_id CHAR(7), \
    interactee_id CHAR(7), \
    PRIMARY KEY(interactor_id,interactee_id), \
    FOREIGN KEY (interactor_id) REFERENCES Drug(drugbank_id) ON DELETE CASCADE ON UPDATE CASCADE, \
    FOREIGN KEY (interactee_id) REFERENCES Drug(drugbank_id) ON DELETE CASCADE ON UPDATE CASCADE)")

cur.execute("CREATE TABLE SideEffectName( \
    umls_cui CHAR(8), \
    name VARCHAR(30), \
    PRIMARY KEY(umls_cui), \
    UNIQUE(name))")

cur.execute("CREATE TABLE DrugCausedSideEffect( \
    umls_cui CHAR(8), \
    drugbank_id CHAR(7), \
    PRIMARY KEY(umls_cui,drugbank_id), \
    FOREIGN KEY (drugbank_id) REFERENCES Drug(drugbank_id) ON DELETE CASCADE ON UPDATE CASCADE, \
    FOREIGN KEY (umls_cui) REFERENCES SideEffectName(umls_cui) ON DELETE CASCADE ON UPDATE CASCADE)")

cur.execute("CREATE TABLE Points( \
    institute VARCHAR(100), \
    score INTEGER, \
    PRIMARY KEY (institute))")

cur.execute("CREATE TABLE Bindings( \
    reaction_id INTEGER, \
    measure VARCHAR(4), \
    affinity_nM INTEGER, \
    doi VARCHAR(50), \
    drugbank_id CHAR(7), \
    uniprot_id CHAR(6), \
    target_name VARCHAR(100), \
    institute VARCHAR(100), \
    PRIMARY KEY(reaction_id), \
    FOREIGN KEY (drugbank_id) REFERENCES Drug(drugbank_id) ON DELETE CASCADE ON UPDATE CASCADE, \
    FOREIGN KEY (uniprot_id) REFERENCES UniProt(uniprot_id) ON DELETE CASCADE ON UPDATE CASCADE, \
    FOREIGN KEY (institute) REFERENCES Points(institute) ON DELETE CASCADE ON UPDATE CASCADE)")

cur.execute("CREATE TABLE Contributors( \
    reaction_id INTEGER, \
    username VARCHAR(30), \
    institute VARCHAR(100), \
    PRIMARY KEY (reaction_id, username), \
    FOREIGN KEY (reaction_id) REFERENCES Bindings(reaction_id) ON DELETE CASCADE ON UPDATE CASCADE, \
    FOREIGN KEY (username, institute) REFERENCES User(username, institute) ON DELETE CASCADE ON UPDATE CASCADE)")



# To do 1: Add the triggers
cur.execute(
    "create trigger deletedrug after delete on Drug for each row \n " \
    "begin \n" \
    "delete from Interacts where interactee_id=OLD.drugbank_id; \n "\
    "delete from Bindings B where B.drugbank_id=OLD.drugbank_id; \n" \
    "delete from DrugCausedSideEffect S where S.drugbank_id=OLD.drugbank_id; \n "\
    "end \n " )

cur.execute(
    "create trigger deleteprotein after delete on UniProt for each row \n " \
    "begin \n " \
    "delete from Bindings B where B.uniprot_id=OLD.uniprot_id; \n " \
    "end \n ")

cur.execute(
    "create trigger addPoints2 before insert on Contributors for each row \n " \
    "begin \n " \
    "if NOT EXISTS (select username,institute from contributors where NEW.username=username AND NEW.institute=institute) then \n " \
    "begin \n" \
    "update Points P set P.score=P.score+2 where P.institute=NEW.institute; \n " \
    "end; \n" \
    "end if; \n " \
    "end\n " )

cur.execute(
    "create trigger deletePoints2 after delete on Contributors for each row \n " \
    "begin \n " \
    "if NOT EXISTS (select username,institute from contributors where OLD.username=username AND OLD.institute=institute) then \n " \
    "begin \n" \
    "update Points P set P.score=P.score-2 where P.institute=OLD.institute; \n " \
    "end; \n" \
    "end if; \n " \
    "end \n " )


# To do 2: Enforce the constraint that the DatabaseManager table can have at most 5 entries
cur.execute(
    "create trigger limitDatabaseManager after insert on DatabaseManager for each row \n " \
    "begin \n " \
    "if (select count(*) from DatabaseManager)>5 then begin \n " \
    "delete from DatabaseManager D where D.username=NEW.username; \n " \
    "end; \n " \
    "end if; \n " \
    "end\n " )


cur.execute("CREATE TRIGGER addPoints5 before insert on Bindings for each row \n " \
    "begin \n " \
    "if NEW.doi NOT IN (select doi from Bindings) then \n" \
    "begin \n"  \
    "update Points P set P.score=P.score+5 where P.institute=NEW.institute; \n " \
    "end; \n "\
    "end if; \n" \
    "end \n ")

cur.execute("create trigger insertPoint after insert on User for each row \n " \
    "begin \n" \
    "insert ignore into Points values (NEW.institute,0); \n "\
    "end \n ")


cur.execute("CREATE PROCEDURE filterTargets (in Drugid CHAR(7), in Measurement VARCHAR(4),in Minval integer, in Maxval integer) \n" \
    "begin \n" \
    "SELECT uniprot_id,target_name FROM Bindings WHERE drugbank_id=Drugid AND measure=Measurement AND affinity_nM<=MaxVal AND affinity_nM>=Minval;\n" \
    "end \n ")


con.commit()
