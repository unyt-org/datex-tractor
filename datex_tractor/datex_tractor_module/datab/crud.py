from .db import Base, ngin, SessionLocal
from .models import Issue, Codeblock
from sqlalchemy import update


class DBcrud():
    def __init__(self):
        self.session = SessionLocal()

    def close(self):
        self.session.close()

    def create(self):
        try:
            Base.metadata.create_all(bind=ngin)
        except Exception:
            return False
        else:
            return True

    def enter(self, i_number, path, code_block):
        new_entry = Issue(
            path=path,
            i_number=i_number,
        )
        self.session.add(new_entry)

        new_block = Codeblock(
            parent_id=i_number,
            content=code_block,
        )
        self.session.add(new_block)
        self.session.commit()

    def enter_advice(self, i_number, advice):
        stmt = (
            update(Codeblock)
            .where(Codeblock.parent_id == i_number)
            .values(response=advice)
        )
        self.session.execute(stmt)
        self.session.commit()

    def delete(self, i_number):
        issues = self.session.query(
            Issue
        ).filter().where(
            Issue.i_number == i_number
        ).all()
        for issue in issues:
            self.session.delete(issue)
        self.session.commit()

    def get_block(self, i_number):
        block = self.session.query(
            Codeblock
        ).filter().where(
            Codeblock.parent_id == i_number
        ).first()
        return block.response

    def print_self(self):
        issues = self.session.query(Issue).all()
        for issue in issues:
            print(issue)

        blocks = self.session.query(Codeblock).all()
        for block in blocks:
            print(block)
