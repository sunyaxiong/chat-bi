import { Authenticator, Heading, useTheme } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import { useEffect, useRef, useState } from 'react';
import { useQuery } from 'react-query';

import { GetServerSideProps } from 'next';
import { useTranslation } from 'next-i18next';
import { serverSideTranslations } from 'next-i18next/serverSideTranslations';
import Head from 'next/head';

import { useCreateReducer } from '@/hooks/useCreateReducer';

import {
  cleanConversationHistory,
  cleanSelectedConversation,
} from '@/utils/app/clean';
import { DEFAULT_TEMPERATURE } from '@/utils/app/const';
import {
  saveConversation,
  saveConversations,
  updateConversation,
} from '@/utils/app/conversation';
import { saveFolders } from '@/utils/app/folders';
import { savePrompts } from '@/utils/app/prompts';
import { getSettings } from '@/utils/app/settings';

import { Conversation } from '@/types/chat';
import { KeyValuePair } from '@/types/data';
import { FolderInterface, FolderType } from '@/types/folder';
import { Prompt } from '@/types/prompt';

import { Chat } from '@/components/Chat/Chat';
import { Chatbar } from '@/components/Chatbar/Chatbar';
import { Navbar } from '@/components/Mobile/Navbar';
import Promptbar from '@/components/Promptbar';

import HomeContext from './home.context';
import { HomeInitialState, initialState } from './home.state';

import { signOut } from '@aws-amplify/auth';
import '@cloudscape-design/global-styles/index.css';
import { Amplify } from 'aws-amplify';
import { v4 as uuidv4 } from 'uuid';

interface Props {
  serverSideApiKeyIsSet: boolean;
  serverSidePluginKeysSet: boolean;
  defaultModelId: string;
  tokenAuth?: boolean;
  tokenError?: string;
}

const configKey = '__AMPLIFY_CONFIG_JSON__';

const moveUser = () => {
  const loginConfig = localStorage.getItem(configKey);
  if (!loginConfig) {
    return;
  }
  const configObj = JSON.parse(loginConfig);
  const loginId = localStorage.getItem(
    `CognitoIdentityServiceProvider.${configObj.aws_user_pools_web_client_id}.LastAuthUser`,
  );
  localStorage.removeItem(
    `CognitoIdentityServiceProvider.${configObj.aws_user_pools_web_client_id}.${loginId}.idToken`,
  );
  localStorage.removeItem(
    `CognitoIdentityServiceProvider.${configObj.aws_user_pools_web_client_id}.${loginId}.signInDetails`,
  );
  localStorage.removeItem(
    `CognitoIdentityServiceProvider.${configObj.aws_user_pools_web_client_id}.${loginId}.clockDrift`,
  );
  localStorage.removeItem(
    `CognitoIdentityServiceProvider.${configObj.aws_user_pools_web_client_id}.${loginId}.refreshToken`,
  );
  localStorage.removeItem(
    `CognitoIdentityServiceProvider.${configObj.aws_user_pools_web_client_id}.${loginId}.accessToken`,
  );
};
const setCognitoConfig = async () => {
  let configDataStr = window.localStorage.getItem(configKey);
  if (configDataStr) {
    const configData = JSON.parse(configDataStr);
    if (configData && configData.aws_user_pools_id) {
      Amplify.configure(configData);
      return;
    }
  }
  if (!process.env.NEXT_PUBLIC_USER_POOL_ID) {
    fetch('/api/getConfig')
      .then((respone) => respone.json())
      .then((result) => {
        const configData = {
          aws_project_region: result.region,
          aws_user_pools_id: result.userPoolId,
          aws_user_pools_web_client_id: result.userPoolClientId,
          aws_cognito_region: result.region,
        };
        Amplify.configure(configData);
        window.localStorage.setItem(configKey, JSON.stringify(configData));
      });
  } else {
    const configData = {
      aws_project_region: process.env.NEXT_PUBLIC_REGION,
      aws_user_pools_id: process.env.NEXT_PUBLIC_USER_POOL_ID,
      aws_user_pools_web_client_id: process.env.NEXT_PUBLIC_USER_CLIENT_ID,
      aws_cognito_region: process.env.NEXT_PUBLIC_REGION,
    };
    Amplify.configure(configData);
    localStorage.setItem(configKey, JSON.stringify(configData));
  }
  try {
    await signOut();
  } catch (error) {}
  window.onbeforeunload = (e) => {
    const alertTxt = '刷新需要重新登录';
    e.returnValue = alertTxt;
    return alertTxt;
  };
};
const components = {
  SignIn: {
    Header() {
      const { tokens } = useTheme();
      useEffect(() => {
        moveUser();
        setCognitoConfig();
      }, []);

      return (
        <Heading
          padding={`${tokens.space.xl} 0 0 ${tokens.space.xl}`}
          level={3}
        >
          登录
        </Heading>
      );
    },
  },
};

const Home = ({
  serverSideApiKeyIsSet,
  serverSidePluginKeysSet,
  defaultModelId,
  tokenAuth = false,
  tokenError,
}: Props) => {
  const { t } = useTranslation('chat');
  const [isTokenVerifying, setIsTokenVerifying] = useState(false);
  const [tokenAuthSuccess, setTokenAuthSuccess] = useState(tokenAuth);

  const contextValue = useCreateReducer<HomeInitialState>({
    initialState,
  });

  const {
    state: {
      apiKey,
      lightMode,
      folders,
      conversations,
      selectedConversation,
      prompts,
      temperature,
    },
    dispatch,
  } = contextValue;

  const stopConversationRef = useRef<boolean>(false);

  const { data, error, refetch } = useQuery(
    ['GetModels', apiKey, serverSideApiKeyIsSet],
    ({ signal }) => {
      if (!apiKey && !serverSideApiKeyIsSet) return null;

      // return getModels(
      //   {
      //     key: apiKey,
      //   },
      //   signal,
      // );
    },
    { enabled: true, refetchOnMount: false },
  );

  // setCognitoConfig();
  useEffect(() => {
    if (data) dispatch({ field: 'models' as any, value: data });
  }, [data, dispatch]);

  useEffect(() => {
    setCognitoConfig();
    return () => {
      moveUser();
      setCognitoConfig();
    };
  }, []);

  // Token验证逻辑
  useEffect(() => {
    const verifyUrlToken = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      
      if (token && !tokenAuthSuccess) {
        setIsTokenVerifying(true);
        
        try {
          const response = await fetch('/api/auth/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token }),
          });
          
          if (response.ok) {
            setTokenAuthSuccess(true);
            // 删除URL中的token参数
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.delete('token');
            window.history.replaceState({}, '', newUrl.pathname + newUrl.search);
          }
        } catch (error) {
          console.error('Token verification failed:', error);
        } finally {
          setIsTokenVerifying(false);
        }
      }
    };
    
    verifyUrlToken();
  }, [tokenAuthSuccess]);

  // FETCH MODELS ----------------------------------------------

  const handleSelectConversation = (conversation: Conversation) => {
    dispatch({
      field: 'selectedConversation',
      value: conversation,
    });

    saveConversation(conversation);
  };

  // FOLDER OPERATIONS  --------------------------------------------

  const handleCreateFolder = (name: string, type: FolderType) => {
    const newFolder: FolderInterface = {
      id: uuidv4(),
      name,
      type,
    };

    const updatedFolders = [...folders, newFolder];

    dispatch({ field: 'folders', value: updatedFolders });
    saveFolders(updatedFolders);
  };

  const handleDeleteFolder = (folderId: string) => {
    const updatedFolders = folders.filter((f) => f.id !== folderId);
    dispatch({ field: 'folders', value: updatedFolders });
    saveFolders(updatedFolders);

    const updatedConversations: Conversation[] = conversations.map((c) => {
      if (c.folderId === folderId) {
        return {
          ...c,
          folderId: null,
        };
      }

      return c;
    });

    dispatch({ field: 'conversations', value: updatedConversations });
    saveConversations(updatedConversations);

    const updatedPrompts: Prompt[] = prompts.map((p) => {
      if (p.folderId === folderId) {
        return {
          ...p,
          folderId: null,
        };
      }

      return p;
    });

    dispatch({ field: 'prompts', value: updatedPrompts });
    savePrompts(updatedPrompts);
  };

  const handleUpdateFolder = (folderId: string, name: string) => {
    const updatedFolders = folders.map((f) => {
      if (f.id === folderId) {
        return {
          ...f,
          name,
        };
      }

      return f;
    });

    dispatch({ field: 'folders', value: updatedFolders });

    saveFolders(updatedFolders);
  };

  // CONVERSATION OPERATIONS  --------------------------------------------

  const handleNewConversation = () => {
    const lastConversation = conversations[conversations.length - 1];

    const newConversation: Conversation = {
      id: uuidv4(),
      name: t('New Conversation'),
      messages: [],
      model: 'Amazon_bedrock',
      temperature: lastConversation?.temperature ?? DEFAULT_TEMPERATURE,
      folderId: null,
    };

    const updatedConversations = [...conversations, newConversation];

    dispatch({ field: 'selectedConversation', value: newConversation });
    dispatch({ field: 'conversations', value: updatedConversations });

    saveConversation(newConversation);
    saveConversations(updatedConversations);

    dispatch({ field: 'loading', value: false });
  };

  const handleUpdateConversation = (
    conversation: Conversation,
    data: KeyValuePair,
  ) => {
    const updatedConversation = {
      ...conversation,
      [data.key]: data.value,
    };

    const { single, all } = updateConversation(
      updatedConversation,
      conversations,
    );

    dispatch({ field: 'selectedConversation', value: single });
    dispatch({ field: 'conversations', value: all });
  };

  // EFFECTS  --------------------------------------------

  useEffect(() => {
    if (window.innerWidth < 640) {
      dispatch({ field: 'showChatbar', value: false });
    }
  }, [selectedConversation]);

  useEffect(() => {
    defaultModelId &&
      dispatch({ field: 'defaultModelId', value: defaultModelId });
    serverSideApiKeyIsSet &&
      dispatch({
        field: 'serverSideApiKeyIsSet',
        value: serverSideApiKeyIsSet,
      });
    serverSidePluginKeysSet &&
      dispatch({
        field: 'serverSidePluginKeysSet',
        value: serverSidePluginKeysSet,
      });
  }, [defaultModelId, serverSideApiKeyIsSet, serverSidePluginKeysSet]);

  // ON LOAD --------------------------------------------

  useEffect(() => {
    setCognitoConfig();
    const settings = getSettings();
    if (settings.theme) {
      dispatch({
        field: 'lightMode',
        value: settings.theme,
      });
    }

    const apiKey = localStorage.getItem('apiKey');

    if (window.innerWidth < 640) {
      dispatch({ field: 'showChatbar', value: false });
      dispatch({ field: 'showPromptbar', value: false });
    }

    const showChatbar = localStorage.getItem('showChatbar');
    if (showChatbar) {
      dispatch({ field: 'showChatbar', value: showChatbar === 'true' });
    }

    const showPromptbar = localStorage.getItem('showPromptbar');
    if (showPromptbar) {
      dispatch({ field: 'showPromptbar', value: showPromptbar === 'true' });
    }

    const folders = localStorage.getItem('folders');
    if (folders) {
      dispatch({ field: 'folders', value: JSON.parse(folders) });
    }

    // 动态加载预制提示词
    const loadDefaultPrompts = async () => {
      try {
        const response = await fetch('/api/getDefaultPrompt');
        if (response.ok) {
          const defaultPrompts = await response.json();
          const formattedPrompts = defaultPrompts.map((item: any, index: number) => ({
            id: `default-${index}`,
            name: item.name,
            description: item.description || '',
            content: item.content,
            folderId: null,
          }));
          dispatch({ field: 'prompts', value: formattedPrompts });
          // 保存到localStorage作为缓存
          localStorage.setItem('prompts', JSON.stringify(formattedPrompts));
        } else {
          // API失败时使用localStorage缓存
          const prompts = localStorage.getItem('prompts');
          if (prompts) {
            dispatch({ field: 'prompts', value: JSON.parse(prompts) });
          }
        }
      } catch (error) {
        console.error('Failed to load default prompts:', error);
        // 错误时使用localStorage缓存
        const prompts = localStorage.getItem('prompts');
        if (prompts) {
          dispatch({ field: 'prompts', value: JSON.parse(prompts) });
        }
      }
    };
    
    loadDefaultPrompts();

    const conversationHistory = localStorage.getItem('conversationHistory');
    if (conversationHistory) {
      const parsedConversationHistory: Conversation[] =
        JSON.parse(conversationHistory);
      const cleanedConversationHistory = cleanConversationHistory(
        parsedConversationHistory,
      );

      dispatch({ field: 'conversations', value: cleanedConversationHistory });
    }

    const selectedConversation = localStorage.getItem('selectedConversation');
    if (selectedConversation) {
      const parsedSelectedConversation: Conversation =
        JSON.parse(selectedConversation);
      const cleanedSelectedConversation = cleanSelectedConversation(
        parsedSelectedConversation,
      );

      dispatch({
        field: 'selectedConversation',
        value: cleanedSelectedConversation,
      });
    } else {
      const lastConversation = conversations[conversations.length - 1];
      dispatch({
        field: 'selectedConversation',
        value: {
          id: uuidv4(),
          name: t('New Conversation'),
          messages: [],
          model: 'Amazon_bedrock',
          temperature: lastConversation?.temperature ?? DEFAULT_TEMPERATURE,
          folderId: null,
        },
      });
    }
  }, [
    defaultModelId,
    dispatch,
    serverSideApiKeyIsSet,
    serverSidePluginKeysSet,
  ]);

  // Token验证失败时显示错误页面
  if (tokenError) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-100">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">访问被拒绝</h1>
          <p className="text-gray-700">{tokenError}</p>
        </div>
      </div>
    );
  }

  // Token验证中显示加载状态
  if (isTokenVerifying) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h1 className="text-xl font-semibold text-gray-800 mb-2">正在验证访问权限</h1>
          <p className="text-gray-600">请稍候...</p>
        </div>
      </div>
    );
  }

  // Token验证成功时直接显示应用界面
  if (tokenAuthSuccess) {
    return (
      <HomeContext.Provider
        value={{
          ...contextValue,
          handleNewConversation,
          handleCreateFolder,
          handleDeleteFolder,
          handleUpdateFolder,
          handleSelectConversation,
          handleUpdateConversation,
          signOut: async () => { 
            await fetch('/api/auth/logout', { method: 'POST' });
            localStorage.clear(); 
            window.location.reload();
          },
          user: { username: 'token-user' },
        }}
      >
        <Head>
          <title>AI for BI</title>
          <meta
            name="description"
            content="AI for BI, a tool for converting natural language into SQL, powered by aws bedrock."
          />
          <meta
            name="viewport"
            content="height=device-height ,width=device-width, initial-scale=1, user-scalable=no"
          />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        {selectedConversation && (
          <main
            className={`flex h-screen w-screen flex-col text-sm text-white dark:text-white ${lightMode}`}
          >
            <div className="fixed top-0 w-full sm:hidden">
              <Navbar
                selectedConversation={selectedConversation}
                onNewConversation={handleNewConversation}
              />
            </div>

            <div className="flex h-full w-full pt-[48px] sm:pt-0">
              <Chatbar />

              <div className="flex flex-1">
                <Chat stopConversationRef={stopConversationRef} />
              </div>

              <Promptbar />
            </div>
          </main>
        )}
      </HomeContext.Provider>
    );
  }

  // 默认使用Cognito认证
  return (
    <Authenticator hideSignUp components={components}>
      {({ signOut, user }) => {
        return (
          <HomeContext.Provider
            value={{
              ...contextValue,
              handleNewConversation,
              handleCreateFolder,
              handleDeleteFolder,
              handleUpdateFolder,
              handleSelectConversation,
              handleUpdateConversation,
              signOut,
              user,
            }}
          >
            <Head>
              <title>AI for BI</title>
              <meta
                name="description"
                content="AI for BI, a tool for converting natural language into SQL, powered by aws bedrock."
              />
              <meta
                name="viewport"
                content="height=device-height ,width=device-width, initial-scale=1, user-scalable=no"
              />
              <link rel="icon" href="/favicon.ico" />
            </Head>
            {selectedConversation && (
              <main
                className={`flex h-screen w-screen flex-col text-sm text-white dark:text-white ${lightMode}`}
              >
                <div className="fixed top-0 w-full sm:hidden">
                  <Navbar
                    selectedConversation={selectedConversation}
                    onNewConversation={handleNewConversation}
                  />
                </div>

                <div className="flex h-full w-full pt-[48px] sm:pt-0">
                  <Chatbar />

                  <div className="flex flex-1">
                    <Chat stopConversationRef={stopConversationRef} />
                  </div>

                  <Promptbar />
                </div>
              </main>
            )}
          </HomeContext.Provider>
        );
      }}
    </Authenticator>
  );
};
export default Home;

export const getServerSideProps: GetServerSideProps = async ({ locale, query, req }) => {
  const defaultModelId = 'Amazon_bedrock';
  let serverSidePluginKeysSet = false;

  // Token验证在前端处理

  // 检查会话状态
  const sessionCookie = req.cookies.session;
  let tokenAuth = false;

  if (sessionCookie) {
    try {
      const jwt = await import('jsonwebtoken');
      const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
      const decoded = jwt.verify(sessionCookie, JWT_SECRET) as any;
      
      if (decoded.authenticated && decoded.exp > Math.floor(Date.now() / 1000)) {
        tokenAuth = true;
      }
    } catch (error) {
      // JWT验证失败
      tokenAuth = false;
    }
  }

  return {
    props: {
      serverSideApiKeyIsSet: !!process.env.OPENAI_API_KEY,
      defaultModelId,
      serverSidePluginKeysSet,
      tokenAuth,
      ...(await serverSideTranslations(locale ?? 'en', [
        'common',
        'chat',
        'sidebar',
        'markdown',
        'promptbar',
        'settings',
      ])),
    },
  };
};
