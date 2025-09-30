"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui";
import { Card } from "@/components/ui";
import { Input } from "@/components/ui";
// import { AppLayout } from "@/components/layout";

interface User {
  id: string;
  email: string;
  username: string;
  provider: string;
  is_verified: boolean;
  created_at: string;
  last_login: string | null;
}

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: ''
  });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      setLoading(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // 模擬使用者資料
      const mockUser: User = {
        id: "user123",
        email: "user@example.com",
        username: "旅遊達人",
        provider: "email",
        is_verified: true,
        created_at: "2024-01-01T00:00:00Z",
        last_login: "2024-01-20T15:30:00Z"
      };

      setUser(mockUser);
      setFormData({
        username: mockUser.username,
        email: mockUser.email
      });
    } catch (error) {
      console.error("載入使用者資料失敗:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setUser(prev => prev ? { ...prev, username: formData.username } : null);
      setEditing(false);
      alert("個人資料已更新！");
    } catch (error) {
      console.error("更新失敗:", error);
      alert("更新失敗，請稍後再試");
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      alert("新密碼與確認密碼不一致");
      return;
    }

    if (passwordForm.newPassword.length < 6) {
      alert("新密碼至少需要 6 個字元");
      return;
    }

    try {
      setSaving(true);
      
      // 模擬 API 呼叫
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setShowPasswordForm(false);
      alert("密碼已更新！");
    } catch (error) {
      console.error("密碼更新失敗:", error);
      alert("密碼更新失敗，請稍後再試");
    } finally {
      setSaving(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
        <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-lg text-slate-600 dark:text-slate-300">載入個人資料中...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
        <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg text-slate-600 dark:text-slate-300">載入使用者資料失敗</p>
            <Button onClick={() => router.push('/login')} className="mt-4">
              重新登入
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
      <div className="min-h-[calc(100vh-80px)] bg-gradient-to-br from-primary-50 to-primary-100 dark:from-slate-900 dark:to-slate-800">
        <div className="container mx-auto px-4 py-8 max-w-2xl">
        {/* 頁面標題 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            個人資料
          </h1>
          <p className="text-slate-600 dark:text-slate-300">
            管理您的帳戶資訊和設定
          </p>
        </div>

        <div className="space-y-6">
          {/* 基本資料 */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                基本資料
              </h2>
              {!editing && (
                <Button
                  variant="outline"
                  onClick={() => setEditing(true)}
                >
                  編輯
                </Button>
              )}
            </div>

            {editing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    使用者名稱
                  </label>
                  <Input
                    type="text"
                    value={formData.username}
                    onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                    placeholder="請輸入使用者名稱"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Email（不可修改）
                  </label>
                  <Input
                    type="email"
                    value={formData.email}
                    disabled
                    className="bg-slate-100 dark:bg-slate-700"
                  />
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                    Email 地址無法修改
                  </p>
                </div>

                <div className="flex justify-end space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setEditing(false);
                      setFormData({
                        username: user.username,
                        email: user.email
                      });
                    }}
                  >
                    取消
                  </Button>
                  <Button
                    onClick={handleSaveProfile}
                    disabled={saving}
                  >
                    {saving ? '儲存中...' : '儲存'}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      使用者名稱
                    </label>
                    <p className="text-slate-900 dark:text-white">{user.username}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      Email
                    </label>
                    <p className="text-slate-900 dark:text-white">{user.email}</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      註冊時間
                    </label>
                    <p className="text-slate-600 dark:text-slate-300">
                      {formatDate(user.created_at)}
                    </p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                      最後登入
                    </label>
                    <p className="text-slate-600 dark:text-slate-300">
                      {user.last_login ? formatDate(user.last_login) : '從未登入'}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
                    帳戶狀態
                  </label>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      user.is_verified
                        ? 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
                        : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
                    }`}>
                      {user.is_verified ? '已驗證' : '未驗證'}
                    </span>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                      {user.provider === 'email' ? 'Email 註冊' : 'OAuth 註冊'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </Card>

          {/* 密碼設定 */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
                密碼設定
              </h2>
              {!showPasswordForm && (
                <Button
                  variant="outline"
                  onClick={() => setShowPasswordForm(true)}
                >
                  修改密碼
                </Button>
              )}
            </div>

            {showPasswordForm ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    目前密碼
                  </label>
                  <Input
                    type="password"
                    value={passwordForm.currentPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, currentPassword: e.target.value }))}
                    placeholder="請輸入目前密碼"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    新密碼
                  </label>
                  <Input
                    type="password"
                    value={passwordForm.newPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, newPassword: e.target.value }))}
                    placeholder="請輸入新密碼（至少 6 個字元）"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    確認新密碼
                  </label>
                  <Input
                    type="password"
                    value={passwordForm.confirmPassword}
                    onChange={(e) => setPasswordForm(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    placeholder="請再次輸入新密碼"
                  />
                </div>

                <div className="flex justify-end space-x-3">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowPasswordForm(false);
                      setPasswordForm({
                        currentPassword: '',
                        newPassword: '',
                        confirmPassword: ''
                      });
                    }}
                  >
                    取消
                  </Button>
                  <Button
                    onClick={handleChangePassword}
                    disabled={saving}
                  >
                    {saving ? '更新中...' : '更新密碼'}
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-16 h-16 bg-slate-100 dark:bg-slate-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                </div>
                <p className="text-slate-600 dark:text-slate-300">
                  點擊「修改密碼」來更新您的密碼
                </p>
              </div>
            )}
          </Card>

          {/* 偏好設定連結 */}
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-slate-900 dark:text-white mb-2">
                  偏好設定
                </h2>
                <p className="text-slate-600 dark:text-slate-300">
                  設定您的旅遊偏好，讓行程推薦更符合您的需求
                </p>
              </div>
              <Button
                onClick={() => router.push('/profile/preferences')}
              >
                前往設定
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
