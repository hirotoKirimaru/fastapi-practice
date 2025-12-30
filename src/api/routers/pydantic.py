# import orjson
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

router = APIRouter()


class BaseModelA(BaseModel):
    pass


class BaseModelB(BaseModel):
    ...
    # model_config = ConfigDict(
    #     json_serializer=orjson.dumps
    # )


# GitHubユーザAPIの深い構造を再現
class Repository(BaseModelA):
    id: int
    name: str
    full_name: str
    private: bool
    html_url: str
    description: str


class Organization(BaseModelA):
    login: str
    id: int
    url: str
    repos_url: str


class UserResponse(BaseModelA):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
    name: str
    company: str
    blog: str
    location: str
    email: str
    hireable: bool
    bio: str
    twitter_username: str
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: str
    updated_at: str
    repositories: list[Repository]
    organizations: list[Organization]
    metadata: dict[str, str]


class RepositoryB(BaseModelB):
    id: int
    name: str
    full_name: str
    private: bool
    html_url: str
    description: str


class OrganizationB(BaseModelB):
    login: str
    id: int
    url: str
    repos_url: str


class UserResponseB(BaseModelB):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool
    name: str
    company: str
    blog: str
    location: str
    email: str
    hireable: bool
    bio: str
    twitter_username: str
    public_repos: int
    public_gists: int
    followers: int
    following: int
    created_at: str
    updated_at: str
    repositories: list[RepositoryB]
    organizations: list[OrganizationB]
    metadata: dict[str, str]


def generate_deep_response():
    return UserResponse(
        login="octocat",
        id=1,
        node_id="MDQ6VXNlcjE=",
        avatar_url="https://github.com/images/error/octocat_happy.gif",
        gravatar_id="",
        url="https://api.github.com/users/octocat",
        html_url="https://github.com/octocat",
        followers_url="https://api.github.com/users/octocat/followers",
        following_url="https://api.github.com/users/octocat/following{/other_user}",
        gists_url="https://api.github.com/users/octocat/gists{/gist_id}",
        starred_url="https://api.github.com/users/octocat/starred{/owner}{/repo}",
        subscriptions_url="https://api.github.com/users/octocat/subscriptions",
        organizations_url="https://api.github.com/users/octocat/orgs",
        repos_url="https://api.github.com/users/octocat/repos",
        events_url="https://api.github.com/users/octocat/events{/privacy}",
        received_events_url="https://api.github.com/users/octocat/received_events",
        type="User",
        site_admin=False,
        name="monalisa octocat",
        company="GitHub",
        blog="https://github.com/blog",
        location="San Francisco",
        email="octocat@github.com",
        hireable=False,
        bio="There once was...",
        twitter_username="monatheoctocat",
        public_repos=2,
        public_gists=1,
        followers=20,
        following=0,
        created_at="2008-01-14T04:33:35Z",
        updated_at="2008-01-14T04:33:35Z",
        repositories=[
            Repository(
                id=1300192,
                name="Spoon-Knife",
                full_name="octocat/Spoon-Knife",
                private=False,
                html_url="https://github.com/octocat/Spoon-Knife",
                description="Test repository",
            )
        ],
        organizations=[
            Organization(
                login="github",
                id=1,
                url="https://api.github.com/orgs/github",
                repos_url="https://api.github.com/orgs/github/repos",
            )
        ],
        metadata={
            "rate_limit": "1000",
            "remaining": "990",
            "api_version": "2022-11-28",
        },
    ).model_dump()


@router.get("/pydantic_only", response_model=UserResponse)
async def pydantic_only():
    return UserResponse(**generate_deep_response())


@router.get("/pydantic_with_orjson", response_model=UserResponseB)
async def with_orjson():
    # return UserResponseB(**generate_deep_response())
    return ORJSONResponse(generate_deep_response())
