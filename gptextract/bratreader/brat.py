import os

preannotated_ents = (
            'PROBLEM',
            'TREATMENT',
            'TEST',
            'SectionAnnotate',
            'SectionSkip'
        )


class Entity:
    def __init__(self, idx, ent_type, start, end, text):
        self.idx = idx
        self.type = ent_type
        self.start = start
        self.end = end
        self.text = text

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_idx(self):
        return self.idx

    def get_type(self):
        return self.type

    def get_text(self):
        return self.text

    def __repr__(self):
        return self.idx + "\t" + self.type + "\t" + self.text


class Relation:
    def __init__(self, idx, rel_type, ent1, ent2, bidir):
        self.idx = idx
        self.type = rel_type
        self.ent1 = ent1
        self.ent2 = ent2
        self.bidir = bidir

    def is_bidirectional(self):
        return self.bidir

    def get_idx(self):
        return self.idx

    def get_source_ent_idx(self):
        return self.ent1

    def get_dest_ent_idx(self):
        return self.ent2

    def get_type(self):
        return self.type

    def __repr__(self):
        return self.idx + "\t" + self.type + "\t" + self.ent1.text + "\t" + self.ent2.text


class Attribute:
    def __init__(self, idx, att_type, ent, val):
        self.idx = idx
        self.type = att_type
        self.ent = ent
        self.val = val

    def __repr__(self):
        return self.idx + "\t" + self.type + "\t" + self.ent.text + "\t" + self.val

    def get_entity(self):
        return self.ent

    def get_idx(self):
        return self.idx

    def get_type(self):
        return self.type

    def get_val(self):
        return self.val


class Document:
    def __init__(self, doc_idx, text, entities, relations, attributes):
        self.doc_idx = doc_idx
        self.text = text
        self.entities = entities # list of entities
        self.relations = relations # list of relations
        self.attributes = attributes  # list of attributes

    @classmethod
    def read(cls, doc_idx, doc_dir):
        cls.doc_idx = doc_idx
        with open(os.path.join(doc_dir, doc_idx+'.txt')) as f_text:
            text = f_text.read().replace('', ' ')

        # TODO: Make entities dictionary instead of / in addition to list?
        entities, relations, attributes = list(), list(), list()

        with open(os.path.join(doc_dir, doc_idx + '.ann')) as f_ann:
            for line in f_ann:
                line = line.split('\t')

                # entities
                if line[0].startswith('T'):
                    ent = cls._get_entity(line)
                    if ent is not None:
                        entities.append(ent)

                # relations
                if line[0].startswith('R') or line[0].startswith('*'):
                    cur_rel = cls._get_relation(line, entities)
                    if cur_rel is not None:
                        relations.append(cur_rel)

                # attributes
                if line[0].startswith('A'):
                    cur_att = cls._get_attribute(line, entities)
                    if cur_att is not None:
                        attributes.append(cur_att)

        return cls(doc_idx, text, entities, relations, attributes)


    @staticmethod
    def _get_entity(line, skip_preannots=True):
        cur_ent_descr = line[1].split()
        cur_ent = cur_ent_descr[0]

        # skip over entities that were not manually added
        if skip_preannots and all(item not in cur_ent for item in preannotated_ents):

            if len(cur_ent_descr) > 3:  # discontinous entities contain multiple offsets, separated by semicolon.
                # we only retain the start offset of the first subpart and end of the last subpart.
                # do not use start and end offsets to get string representation in this case.
                start = int(" ".join(cur_ent_descr[1:]).split(';')[0].split(' ')[0])
                end = int(" ".join(cur_ent_descr[1:]).split(';')[-1].split(' ')[-1])

            else:
                start = int(cur_ent_descr[1])
                end = int(cur_ent_descr[2])

            return Entity(idx=line[0],
                          ent_type=cur_ent,
                          start=start,
                          end=end,
                          text=line[-1].replace('', ' ')
                          )

    @staticmethod
    def _get_relation(line, entities):
        rel_descr = line[1].split()

        # TODO: figure out the * and the direction

        entity1 = rel_descr[1].split(':')[-1]
        entity2 = rel_descr[2].split(':')[-1]

        ent1_obj, ent2_obj = None, None

        for cur_ent in entities:
            if cur_ent.idx == entity1:
                ent1_obj = cur_ent

            if cur_ent.idx == entity2:
                ent2_obj = cur_ent

        if ent1_obj is None or ent2_obj is None:
            return None  # Dangling relation

        return Relation(idx=line[0],  # This can be only * for multiple relations.
                        rel_type=rel_descr[0],
                        ent1=ent1_obj,
                        ent2=ent2_obj,
                        bidir=None,
                        )

    @staticmethod
    def _get_attribute(line, entities):
        attr_descr = line[1].split()

        ent_obj = None
        for cur_ent in entities:
            if cur_ent.idx == attr_descr[1]:
                ent_obj = cur_ent

        if ent_obj is None:
            return None   # Dangling attribute

        return Attribute(idx=line[0],
                         att_type=attr_descr[0],
                         ent=ent_obj,
                         val=attr_descr[2],
                         )


class Collection:
    def __init__(self, docs):
        self.documents = docs

    @classmethod
    def read_collection(cls, coll_dir):
        documents = dict()

        for fname in os.listdir(coll_dir):
            if fname.endswith('.txt'):
                doc_idx = os.path.splitext(os.path.basename(fname))[0]
                ann_file = os.path.join(coll_dir, doc_idx+'.ann')

                if not os.path.exists(ann_file):
                    continue

                cur_doc = Document.read(doc_idx, coll_dir)
                documents[doc_idx] = cur_doc

        return cls(documents)

    def get_document(self, doc_idx):
        if doc_idx in self.documents:
            return self.documents[doc_idx]
        else:
            return None

    def get_section_annots(self, doc_idx, section_start, section_end):
        document = self.get_document(doc_idx)

        section_ents, section_rels, section_atts = list(), list(), list()
        section_ents_idx = set()

        for cur_ent in document.entities:
            if cur_ent.start >= section_start and cur_ent.end <= section_end:
                section_ents.append(cur_ent)
                section_ents_idx.add(cur_ent.idx)

        for cur_rel in document.relations:
            if cur_rel.ent1.idx in section_ents_idx and cur_rel.ent2.idx in section_ents_idx:
                section_rels.append(cur_rel)

        for cur_att in document.attributes:
            if cur_att.ent.idx in section_ents_idx:
                section_atts.append(cur_att)

        return section_ents, section_rels, section_atts







