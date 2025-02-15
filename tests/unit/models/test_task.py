import pytest
from sqlalchemy import Select, select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.exc import DetachedInstanceError

import src.crud
from src import models
from src.models.post import Post
from src.models.task import Done, Task
from src.models.user import User


class TestTask:
    class TestGetTasksWithDone:
        @pytest.mark.asyncio
        async def test_get_single(self, db):
            # Given
            task1 = Task(title="ダミー1")
            db.add(task1)

            await db.commit()
            await db.refresh(task1)

            # WHEN
            actual = await src.crud.task.get_tasks_with_done(db)

            # THEN
            assert len(actual) == 1
            assert actual == [(1, "ダミー1", False)]

        @pytest.mark.asyncio
        async def test_get_multiple(self, db):
            # Given
            task1 = Task(title="ダミー1")
            task2 = Task(title="ダミー2")
            db.add(task1)
            db.add(task2)

            await db.commit()
            await db.refresh(task1)
            await db.refresh(task2)

            # WHEN
            actual = await src.crud.task.get_tasks_with_done(db)

            # THEN
            assert len(actual) == 2
            assert actual == [(1, "ダミー1", False), (2, "ダミー2", False)]

    class TestGetTasksWithDoneInnerJoin:
        @pytest.mark.asyncio
        async def test_get_single(self, db):
            # Given
            task1 = Task(title="ダミー1")
            db.add(task1)

            await db.commit()
            await db.refresh(task1)

            done1 = Done(id=task1.id)
            db.add(done1)

            await db.commit()
            await db.refresh(done1)

            # WHEN
            actual = await src.crud.task.get_tasks_with_done_inner_join(db)

            # THEN
            assert len(actual) == 1
            assert actual == [(1, "ダミー1", True)]

        @pytest.mark.asyncio
        async def test_get_multiple(self, db):
            # Given
            task1 = Task(title="ダミー1")
            task2 = Task(title="ダミー2")
            db.add(task1)
            db.add(task2)

            await db.commit()
            await db.refresh(task1)
            await db.refresh(task2)

            done1 = Done(id=task1.id)
            done2 = Done(id=task2.id)
            db.add(done1)
            db.add(done2)

            await db.commit()
            await db.refresh(done1)
            await db.refresh(done2)

            # WHEN
            actual = await src.crud.task.get_tasks_with_done_inner_join(db)

            # THEN
            assert len(actual) == 2
            assert actual == [(1, "ダミー1", True), (2, "ダミー2", True)]



        class TestExpunge:
            """
            expungeやrefreshを学ぶため
            TODO: 家ではうまくいってしまったので、会社でなぜ発生したかは不明


            """
            class Test1_1:

                async def test_add_expunge(self, db):
                    # Given
                    task1 = Task(title="ダミー1")
                    db.add(task1)
                    await db.flush()

                    query: Select = (select(Task).options(joinedload(Task.done)))
                    actual = (await db.execute(query)).scalars().all()

                    # この時点ではインスタンスは紐づけがない
                    assert task1.done is None

                    done1 = Done(id=task1.id)
                    db.add(done1)
                    await db.flush()

                    # インスタンス側は変更なし
                    assert task1.done is None

                    actual2 = (await db.execute(query)).scalars().all()

                    assert task1.done is None

                    await db.refresh(task1)

                    assert task1.done == done1


                async def test_delete_expunge(self, db):
                    # Given
                    task1 = Task(title="ダミー1")
                    db.add(task1)
                    await db.flush()
                    done1 = Done(id=task1.id)
                    db.add(done1)
                    await db.flush()

                    # この時点ではインスタンスは紐づけがない
                    # と思っていたが、1:1の関係があると、flushの時点でマッピングしにいくらしい
                    assert task1.done == done1

                    query: Select = (select(Task).options(joinedload(Task.done)))
                    # actual = (await db.execute(query)).scalars().all()
                    #
                    # # 検索したのでインスタンスがマッピングされた
                    # assert task1.done == done1
                    # assert actual[0].done == done1

                    await db.delete(done1)
                    await db.flush()


                    # 削除済みだがインスタンスとしては何も変わらない
                    assert task1.done == done1
                    # assert actual[0].done == done1
                    actual2 = (await db.execute(query)).scalars().all()

                    # 再検索してもインスタンスは変わらない
                    assert task1.done == done1
                    assert actual2[0].done == done1

                    # refresh
                    # with pytest.raises(DetachedInstanceError):
                    # これを入れると、task1.doneにアクセスするたびにDetachedInstanceErrorが発生する
                    # await db.refresh(task1)

                    # SQLAlchemyから切り離しても、インスタンスは変わらない
                    db.expunge(task1)
                    await db.flush()

                    assert task1.done == done1
                    assert actual2[0].done == done1

                    # 切り離したうえで再検索したらようやく出現
                    actual3 = (await db.execute(query)).scalars().all()

                    assert task1.done == done1
                    assert actual3[0].done is None

            from sqlalchemy import select
            from sqlalchemy.orm import joinedload

            class TestOneToMany:
                async def test_add_and_expunge(self, db):
                    # ユーザーを作成
                    user = User(name="テストユーザー")
                    db.add(user)
                    await db.flush()

                    # 投稿を作成
                    post1 = Post(title="投稿1", user_id=user.id)
                    post2 = Post(title="投稿2", user_id=user.id)
                    db.add_all([post1, post2])
                    await db.flush()

                    # リレーションシップの確認
                    await db.refresh(user, attribute_names=['posts'])
                    assert len(user.posts) == 2
                    assert user.posts[0].title == "投稿1"
                    assert user.posts[1].title == "投稿2"

                    # 新しい投稿を追加
                    post3 = Post(title="投稿3", user_id=user.id)
                    db.add(post3)
                    await db.flush()

                    # まだインスタンス側は2
                    assert len(user.posts) == 2

                    # userをexpunge
                    db.expunge(user)

                    # 再検索（joinedloadを使用）
                    query = select(User).options(joinedload(User.posts)).where(User.id == user.id)
                    result = await db.execute(query)
                    refreshed_user = result.scalars().first()

                    # 結果の確認
                    assert len(refreshed_user.posts) == 3
                    assert any(post.title == "投稿3" for post in refreshed_user.posts)

                async def test_delete_and_expunge(self, db):
                    # ユーザーと投稿を作成
                    user = User(name="テストユーザー")
                    db.add(user)
                    await db.flush()

                    post1 = Post(title="投稿1", user_id=user.id)
                    post2 = Post(title="投稿2", user_id=user.id)
                    db.add_all([post1, post2])
                    await db.flush()

                    # 最初は2
                    await db.refresh(user, attribute_names=['posts'])
                    assert len(user.posts) == 2

                    # 投稿を削除
                    await db.delete(post1)
                    await db.flush()

                    # この時点では、userのpostsは更新されていない
                    await db.refresh(user, attribute_names=['posts'])
                    assert len(user.posts) == 1

                    # userをexpunge
                    db.expunge(user)

                    # # 再検索（joinedloadを使用）
                    # query = select(User).options(joinedload(User.posts)).where(User.id == user.id)
                    # result = await db.execute(query)
                    # refreshed_user = result.scalars().first()
                    #
                    # # 結果の確認
                    # assert len(refreshed_user.posts) == 1
                    # assert refreshed_user.posts[0].title == "投稿2"