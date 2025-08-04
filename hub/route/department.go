package route

import (
	"net/http"
	"strings"

	"github.com/metacubex/mihomo/config"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
)

// ProxyUserInfo 代理用户信息
type ProxyUserInfo struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Region   string `json:"region"`
}

// DepartmentSecretResponse 部门密钥接口响应
type DepartmentSecretResponse struct {
	DepartmentID string          `json:"department_id"`
	Users        []ProxyUserInfo `json:"users"`
}

func departmentRouter() http.Handler {
	r := chi.NewRouter()
	r.Get("/secret", getDepartmentUsers)
	return r
}

func getDepartmentUsers(w http.ResponseWriter, r *http.Request) {
	// 从查询参数获取密钥
	secret := r.URL.Query().Get("secret")
	if secret == "" {
		render.Status(r, http.StatusBadRequest)
		render.JSON(w, r, newError("Missing secret parameter"))
		return
	}

	// 获取当前配置
	cfg := config.GetRawConfig()
	if cfg == nil {
		render.Status(r, http.StatusInternalServerError)
		render.JSON(w, r, newError("Configuration not available"))
		return
	}

	// 查找部门映射
	departmentID, exists := cfg.DepartmentSecrets[secret]
	if !exists {
		render.Status(r, http.StatusUnauthorized)
		render.JSON(w, r, newError("Invalid secret"))
		return
	}

	// 获取该部门的所有ProxyUser
	users := getDepartmentProxyUsers(departmentID, cfg)

	response := DepartmentSecretResponse{
		DepartmentID: departmentID,
		Users:        users,
	}

	render.JSON(w, r, response)
}

// getDepartmentProxyUsers 获取指定部门的所有代理用户信息
func getDepartmentProxyUsers(departmentID string, cfg *config.RawConfig) []ProxyUserInfo {
	var users []ProxyUserInfo

	// 遍历规则，查找PROXY-USER类型的规则
	for _, rule := range cfg.Rule {
		// 解析规则字符串，格式: "PROXY-USER,username1/username2,PROXY_GROUP"
		parts := strings.Split(rule, ",")
		if len(parts) >= 3 && strings.TrimSpace(parts[0]) == "PROXY-USER" {
			usernames := strings.TrimSpace(parts[1])
			proxyGroup := strings.TrimSpace(parts[2])

			// 解析用户名列表
			userList := strings.Split(usernames, "/")
			for _, username := range userList {
				username = strings.TrimSpace(username)
				if username == "" {
					continue
				}

				// 检查用户是否属于指定部门（这里简化处理，实际可能需要更复杂的映射逻辑）
				if shouldIncludeUser(username, departmentID) {
					region := getRegionFromProxyGroup(proxyGroup, cfg)
					users = append(users, ProxyUserInfo{
						Username: username,
						Password: generatePasswordForUser(username), // 这里需要实现密码生成逻辑
						Region:   region,
					})
				}
			}
		}
	}

	return users
}

// shouldIncludeUser 判断用户是否属于指定部门
func shouldIncludeUser(username, departmentID string) bool {
	// 实现用户-部门映射逻辑
	// 1. 如果用户名包含部门ID，则认为属于该部门
	if strings.Contains(strings.ToLower(username), strings.ToLower(departmentID)) {
		return true
	}

	// 2. 根据用户名前缀判断部门
	userLower := strings.ToLower(username)
	deptLower := strings.ToLower(departmentID)

	// 技术部门
	if deptLower == "tech_dept" && (strings.HasPrefix(userLower, "tech_") || strings.HasPrefix(userLower, "dev_") || strings.HasPrefix(userLower, "engineer_")) {
		return true
	}

	// 销售部门
	if deptLower == "sales_dept" && (strings.HasPrefix(userLower, "sales_") || strings.HasPrefix(userLower, "sale_")) {
		return true
	}

	// 人事部门
	if deptLower == "hr_dept" && (strings.HasPrefix(userLower, "hr_") || strings.HasPrefix(userLower, "human_")) {
		return true
	}

	// 财务部门
	if deptLower == "finance_dept" && (strings.HasPrefix(userLower, "finance_") || strings.HasPrefix(userLower, "accounting_")) {
		return true
	}

	return false
}

// getRegionFromProxyGroup 从代理组名称推断地区
func getRegionFromProxyGroup(proxyGroup string, cfg *config.RawConfig) string {
	proxyGroup = strings.ToUpper(proxyGroup)

	// 根据代理组名称推断地区
	if strings.Contains(proxyGroup, "US") || strings.Contains(proxyGroup, "AMERICA") {
		return "美国"
	} else if strings.Contains(proxyGroup, "HK") || strings.Contains(proxyGroup, "HONGKONG") {
		return "香港"
	} else if strings.Contains(proxyGroup, "JP") || strings.Contains(proxyGroup, "JAPAN") {
		return "日本"
	} else if strings.Contains(proxyGroup, "SG") || strings.Contains(proxyGroup, "SINGAPORE") {
		return "新加坡"
	} else if strings.Contains(proxyGroup, "VIP") {
		return "VIP专线"
	}

	return "未知地区"
}

// generatePasswordForUser 为用户生成密码（这里需要根据实际需求实现）
func generatePasswordForUser(username string) string {
	// 这里应该实现实际的密码生成或查询逻辑
	// 可以从数据库查询、从配置文件读取或使用加密算法生成

	// 示例实现：基于用户名生成固定密码
	// 在实际应用中，应该从安全的存储中获取或生成更安全的密码

	// 简单的密码映射示例
	passwordMap := map[string]string{
		"tech_user1":    "TechPass123!",
		"tech_user2":    "TechPass456!",
		"tech_admin":    "AdminTech789!",
		"sales_user1":   "SalesPass123!",
		"sales_user2":   "SalesPass456!",
		"sales_manager": "ManagerSales789!",
		"hr_user1":      "HRPass123!",
		"hr_user2":      "HRPass456!",
		"finance_user1": "FinancePass123!",
		"finance_user2": "FinancePass456!",
	}

	if password, exists := passwordMap[username]; exists {
		return password
	}

	// 如果没有预定义密码，生成一个基于用户名的密码
	return "Pass_" + username + "_2024!"
}
