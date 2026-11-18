/** バックエンドの GraphQL（src/graphql/schema.py）に投げる操作と、その結果の型 */

export type GqlUser = { id: number; name: string; email: string };
export type GqlPost = { id: number; title: string; userId: number };

export const HELLO_QUERY = /* GraphQL */ `
  query Hello($name: String!) {
    hello(name: $name)
  }
`;
export type HelloResult = { hello: string };

/** 要ログイン */
export const ME_QUERY = /* GraphQL */ `
  query Me {
    me {
      id
      name
      email
    }
  }
`;
export type MeResult = { me: GqlUser };

export const USER_QUERY = /* GraphQL */ `
  query User($id: Int!) {
    user(id: $id) {
      id
      name
      email
    }
  }
`;
export type UserResult = { user: GqlUser | null };

export const POSTS_QUERY = /* GraphQL */ `
  query Posts {
    posts {
      id
      title
      userId
    }
  }
`;
export type PostsResult = { posts: GqlPost[] };

/** 要ログイン。ログイン中のユーザの投稿として作る */
export const CREATE_POST_MUTATION = /* GraphQL */ `
  mutation CreatePost($title: String!) {
    createPost(title: $title) {
      id
      title
      userId
    }
  }
`;
export type CreatePostResult = { createPost: GqlPost };
