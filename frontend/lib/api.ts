import axios from "axios";
import type {
  DomainAdminStats,
  MailboxListItem,
  MailboxCreateRequest,
  MailboxCreateResponse,
  DNSStatus,
  DnsRecord,
} from "@/types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const axiosInstance = axios.create({
  baseURL: API_URL,
});

// Lazy-load auth store to avoid circular dependency
function getAuthState() {
  // eslint-disable-next-line @typescript-eslint/no-var-requires
  const { useAuth } = require("@/hooks/useAuth");
  return useAuth.getState();
}

axiosInstance.interceptors.request.use(
  (config) => {
    const token = getAuthState().accessToken;
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = getAuthState().refreshToken;
        if (!refreshToken) {
          getAuthState().logout();
          return Promise.reject(error);
        }
        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token } = response.data;
        getAuthState().setTokens(access_token, refresh_token);
        originalRequest.headers["Authorization"] = "Bearer " + access_token;
        return axiosInstance(originalRequest);
      } catch (refreshError) {
        getAuthState().logout();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);

// ─── Auth ─────────────────────────────────────────────────────────────────────
export const login = async (credentials: {
  email: string;
  password: string;
}) => {
  const data = (await axiosInstance.post("/auth/login", credentials)).data;
  // Backend may return { tokens: { access_token, refresh_token, ... }, requires_totp, ... }
  // OR a flat { access_token, refresh_token, ... }
  // Normalize to always expose access_token / refresh_token at the top level.
  if (data?.tokens && !data.access_token) {
    return { ...data, ...data.tokens };
  }
  return data;
};

export const logout = async () =>
  (await axiosInstance.post("/auth/logout")).data;

export const refreshToken = async (token: string) =>
  (await axiosInstance.post("/auth/refresh", { refresh_token: token })).data;

export const requestPasswordReset = async (
  input: string | { email: string },
) => {
  const email = typeof input === "string" ? input : input.email;
  // Backend route: POST /auth/forgot-password
  return (await axiosInstance.post("/auth/forgot-password", { email })).data;
};

export const resetPassword = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/auth/reset-password", data)).data;

export const verifyTotp = async (data: {
  temp_token: string;
  code: string;
  is_backup_code: boolean;
}) =>
  // Backend route: POST /auth/totp/verify
  (await axiosInstance.post("/auth/totp/verify", data)).data;

export const getInvitedUserData = async (token: string) =>
  (await axiosInstance.get(`/auth/invite/${token}`)).data;

export const acceptInvite = async (data: {
  token: string;
  [key: string]: unknown;
}) => {
  const { token, ...body } = data;
  return (await axiosInstance.post(`/auth/invite/${token}`, body)).data;
};

// Backend route: GET /auth/me
export const getMe = async () => (await axiosInstance.get("/auth/me")).data;

// ─── Whitelabel ───────────────────────────────────────────────────────────────
// Backend route: GET /domain-admin/whitelabel?domain=X  (public, no auth required)
export const getWhitelabelSettings = async (domain: string) =>
  (await axiosInstance.get("/domain-admin/whitelabel", { params: { domain } }))
    .data;

// Backend route: PATCH /domain-admin/whitelabel
export const updateWhitelabel = async (data: Record<string, unknown>) =>
  (await axiosInstance.patch("/domain-admin/whitelabel", data)).data;

// ─── Super Admin ──────────────────────────────────────────────────────────────
export const getSuperAdminStats = async () =>
  (await axiosInstance.get("/super-admin/stats")).data;

export const getSuperAdminDomains = async (params?: Record<string, unknown>) =>
  (await axiosInstance.get("/super-admin/domains", { params })).data;

export const createDomain = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/super-admin/domains", data)).data;

export const deleteDomain = async (domainId: string) =>
  (await axiosInstance.delete(`/super-admin/domains/${domainId}`)).data;

export const suspendDomain = async (domainId: string) =>
  (await axiosInstance.patch(`/super-admin/domains/${domainId}/suspend`)).data;

export const unsuspendDomain = async (domainId: string) =>
  (await axiosInstance.patch(`/super-admin/domains/${domainId}/unsuspend`))
    .data;

export const inviteDomainAdmin = async (data: Record<string, unknown>) =>
  // Backend route: POST /super-admin/domains/invite
  (await axiosInstance.post("/super-admin/domains/invite", data)).data;

export const getSuperAdminBackups = async () =>
  (await axiosInstance.get("/super-admin/backups")).data;

export const createSuperAdminBackup = async () =>
  (await axiosInstance.post("/super-admin/backups")).data;

export const getSuperAdminAuditLogs = async (
  params?: Record<string, unknown>,
) => (await axiosInstance.get("/super-admin/audit-logs", { params })).data;

export const getSuperAdminSettings = async () =>
  (await axiosInstance.get("/super-admin/settings")).data;

export const updateSuperAdminSettings = async (data: Record<string, unknown>) =>
  (await axiosInstance.put("/super-admin/settings", data)).data;

// ─── Domain Admin ─────────────────────────────────────────────────────────────
export const getDomainAdminStats = async (): Promise<DomainAdminStats> =>
  (await axiosInstance.get("/domain-admin/stats")).data;

// Backend route: GET /domain-admin/dns-records — returns { records: DnsRecord[] }
// We unwrap so callers always get a plain array.
export const getDomainDnsRecords = async (): Promise<DnsRecord[]> => {
  const data = (await axiosInstance.get("/domain-admin/dns-records")).data;
  // Normalise: backend wraps in { records: [...] }
  return Array.isArray(data) ? data : (data?.records ?? []);
};

export const getDomainUsers = async () =>
  (await axiosInstance.get("/domain-admin/users")).data;

export const createDomainUser = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/domain-admin/users", data)).data;

export const getDomainMailboxes = async (): Promise<MailboxListItem[]> =>
  (await axiosInstance.get("/domain-admin/mailboxes")).data;

export const createDomainMailbox = async (
  data: MailboxCreateRequest,
): Promise<MailboxCreateResponse> =>
  (await axiosInstance.post("/domain-admin/mailboxes", data)).data;

export const getDomainDnsStatus = async (): Promise<DNSStatus> =>
  (await axiosInstance.get("/domain-admin/dns/status")).data;

export const verifyDomainDns = async () =>
  (await axiosInstance.post("/domain-admin/dns/verify")).data;

export const autoSetupDomainDns = async () =>
  (await axiosInstance.post("/domain-admin/dns/auto")).data;

export const updateDomainMailbox = async (
  id: string,
  data: Record<string, unknown>,
) => (await axiosInstance.patch(`/domain-admin/mailboxes/${id}`, data)).data;

export const deleteDomainMailbox = async (id: string) =>
  (await axiosInstance.delete(`/domain-admin/mailboxes/${id}`)).data;

export const getDomainApiKeys = async () =>
  (await axiosInstance.get("/domain-admin/api-keys")).data;

export const createDomainApiKey = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/domain-admin/api-keys", data)).data;

export const getDomainAuditLogs = async () =>
  (await axiosInstance.get("/domain-admin/audit-logs")).data;

export const getDomainSettings = async () =>
  (await axiosInstance.get("/domain-admin/settings")).data;

export const updateDomainSettings = async (data: Record<string, unknown>) =>
  (await axiosInstance.put("/domain-admin/settings", data)).data;

export const getSharedMailboxes = async () =>
  (await axiosInstance.get("/domain-admin/shared-mailboxes")).data;

// Backend route: PATCH /domain-admin/retention
export const updateRetention = async (data: Record<string, unknown>) =>
  (await axiosInstance.patch("/domain-admin/retention", data)).data;

// Backend route: POST /domain-admin/ediscovery/export
export const createEdiscoveryExport = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/domain-admin/ediscovery/export", data)).data;

export const getEdiscoveryExports = async () =>
  (await axiosInstance.get("/domain-admin/ediscovery")).data;

export const domainBackup = async () =>
  (await axiosInstance.post("/domain-admin/backup")).data;

// ─── Mail ─────────────────────────────────────────────────────────────────────
export const listMail = async (folder: string) =>
  (await axiosInstance.get("/mail", { params: { folder } })).data;

export const getMail = async (id: string) =>
  (await axiosInstance.get(`/mail/${id}`)).data;

export const sendMail = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/mail/send", data)).data;

// ─── User settings ────────────────────────────────────────────────────────────
// Correct paths: /api-keys, /rules, /labels, /templates, /webhooks
export const listApiKeys = async () =>
  (await axiosInstance.get("/api-keys")).data;

export const createApiKey = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/api-keys", data)).data;

export const deleteApiKey = async (id: string) =>
  (await axiosInstance.delete(`/api-keys/${id}`)).data;

export const listRules = async () => (await axiosInstance.get("/rules")).data;

export const createRule = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/rules", data)).data;

export const updateRule = async (id: string, data: Record<string, unknown>) =>
  (await axiosInstance.put(`/rules/${id}`, data)).data;

export const deleteRule = async (id: string) =>
  (await axiosInstance.delete(`/rules/${id}`)).data;

export const listLabels = async () => (await axiosInstance.get("/labels")).data;

export const createLabel = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/labels", data)).data;

export const updateLabel = async (id: string, data: Record<string, unknown>) =>
  (await axiosInstance.put(`/labels/${id}`, data)).data;

export const deleteLabel = async (id: string) =>
  (await axiosInstance.delete(`/labels/${id}`)).data;

export const listTemplates = async () =>
  (await axiosInstance.get("/templates")).data;

export const createTemplate = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/templates", data)).data;

export const updateTemplate = async (
  id: string,
  data: Record<string, unknown>,
) => (await axiosInstance.put(`/templates/${id}`, data)).data;

export const deleteTemplate = async (id: string) =>
  (await axiosInstance.delete(`/templates/${id}`)).data;

export const listWebhooks = async () =>
  (await axiosInstance.get("/webhooks")).data;

export const createWebhook = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/webhooks", data)).data;

export const deleteWebhook = async (id: string) =>
  (await axiosInstance.delete(`/webhooks/${id}`)).data;

export const testWebhook = async (id: string) =>
  (await axiosInstance.post(`/webhooks/${id}/test`)).data;

// Backend route: GET /auth/login-activity
export const getLoginActivity = async () =>
  (await axiosInstance.get("/auth/login-activity")).data;

// ─── Tasks / Notes ────────────────────────────────────────────────────────────
export const listTasks = async () => (await axiosInstance.get("/tasks")).data;

export const createTask = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/tasks", data)).data;

export const updateTask = async (id: string, data: Record<string, unknown>) =>
  (await axiosInstance.put(`/tasks/${id}`, data)).data;

export const deleteTask = async (id: string) =>
  (await axiosInstance.delete(`/tasks/${id}`)).data;

export const listNotes = async () => (await axiosInstance.get("/notes")).data;

export const createNote = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/notes", data)).data;

export const updateNote = async (id: string, data: Record<string, unknown>) =>
  (await axiosInstance.put(`/notes/${id}`, data)).data;

export const deleteNote = async (id: string) =>
  (await axiosInstance.delete(`/notes/${id}`)).data;

// ─── Calendar ─────────────────────────────────────────────────────────────────
export const listCalendarEvents = async () =>
  (await axiosInstance.get("/calendar/events")).data;

export const createCalendarEvent = async (data: Record<string, unknown>) =>
  (await axiosInstance.post("/calendar/events", data)).data;

export const updateCalendarEvent = async (
  id: string,
  data: Record<string, unknown>,
) => (await axiosInstance.put(`/calendar/events/${id}`, data)).data;

export const deleteCalendarEvent = async (id: string) =>
  (await axiosInstance.delete(`/calendar/events/${id}`)).data;

// ─── Unsubscribe ──────────────────────────────────────────────────────────────
export const unsubscribeUser = async (token: string) =>
  (await axiosInstance.post(`/unsubscribe/${token}`)).data;

// ─── Backward-compat aliases ──────────────────────────────────────────────────
export const getAuditLogs = getSuperAdminAuditLogs;
export const getBackupJobs = getSuperAdminBackups;
export const triggerBackup = createSuperAdminBackup;
export const getDomains = getSuperAdminDomains;
export const getSuperAdminDashboard = getSuperAdminStats;
export const getDomainAdminDashboard = getDomainAdminStats;
export const confirmPasswordReset = resetPassword;
export const getInviteInfo = getInvitedUserData;
export const unsubscribe = unsubscribeUser;

// ─── Namespaced api object (for api.xxx() call style) ─────────────────────────
export const api = {
  // Auth
  login,
  logout,
  refreshToken,
  requestPasswordReset,
  resetPassword,
  verifyTotp,
  getInvitedUserData,
  acceptInvite,
  getMe,
  confirmPasswordReset,
  getInviteInfo,

  // Whitelabel
  getWhitelabelSettings,
  updateWhitelabel,

  // Super Admin
  getSuperAdminStats,
  getSuperAdminDomains,
  createDomain,
  deleteDomain,
  suspendDomain,
  unsuspendDomain,
  inviteDomainAdmin,
  getSuperAdminBackups,
  createSuperAdminBackup,
  getSuperAdminAuditLogs,
  getSuperAdminSettings,
  updateSuperAdminSettings,
  getSuperAdminDashboard: getSuperAdminStats,
  getAuditLogs: getSuperAdminAuditLogs,
  getBackupJobs: getSuperAdminBackups,
  triggerBackup: createSuperAdminBackup,
  getDomains: getSuperAdminDomains,

  // Domain Admin
  getDomainAdminStats,
  getDomainAdminDashboard: getDomainAdminStats,
  getDomainDnsRecords,
  getDomainDnsStatus,
  verifyDomainDns,
  autoSetupDomainDns,
  getDomainUsers,
  createDomainUser,
  getDomainMailboxes,
  createDomainMailbox,
  updateDomainMailbox,
  deleteDomainMailbox,
  getDomainApiKeys,
  createDomainApiKey,
  getDomainAuditLogs,
  getDomainSettings,
  updateDomainSettings,
  getSharedMailboxes,
  updateRetention,
  createEdiscoveryExport,
  getEdiscoveryExports,
  domainBackup,

  // Mail
  listMail,
  getMail,
  sendMail,

  // User Settings
  listApiKeys,
  createApiKey,
  deleteApiKey,
  listRules,
  createRule,
  updateRule,
  deleteRule,
  listLabels,
  createLabel,
  updateLabel,
  deleteLabel,
  listTemplates,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  listWebhooks,
  createWebhook,
  deleteWebhook,
  testWebhook,
  getLoginActivity,

  // Tasks / Notes
  listTasks,
  createTask,
  updateTask,
  deleteTask,
  listNotes,
  createNote,
  updateNote,
  deleteNote,

  // Calendar
  listCalendarEvents,
  createCalendarEvent,
  updateCalendarEvent,
  deleteCalendarEvent,

  // Unsubscribe
  unsubscribe: unsubscribeUser,

  // Axios instance for custom calls
  _axios: axiosInstance,
};
