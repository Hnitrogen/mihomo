package route

import (
	"fmt"
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

	fmt.Printf("DepartmentSecrets: %v\n", cfg.DepartmentSecrets)
	// 查找部门映射 - 反向查找，通过department name找到对应的secret key
	var departmentID string
	var secretKey string
	found := false

	for key, value := range cfg.DepartmentSecrets {
		if value == secret {
			departmentID = key // department name 就是我们要的 departmentID
			secretKey = value  // 对应的 secret key
			found = true
			break
		}
	}

	if !found {
		render.Status(r, http.StatusUnauthorized)
		render.JSON(w, r, newError("Invalid department name"))
		return
	}

	fmt.Printf("Found department: %s with secret key: %s\n", departmentID, secretKey)

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

	// 构建用户名到密码的映射
	authMap := make(map[string]string)
	for _, auth := range cfg.Authentication {
		parts := strings.Split(auth, ":")
		if len(parts) == 2 {
			username := strings.TrimSpace(parts[0])
			password := strings.TrimSpace(parts[1])
			authMap[username] = password
		}
	}

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
					// 从authentication中查找对应的密码
					password, exists := authMap[username]
					if !exists {
						continue // 如果找不到密码，跳过这个用户
					}

					region := getRegionFromProxyGroup(proxyGroup)
					users = append(users, ProxyUserInfo{
						Username: username,
						Password: password,
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
	// 根据用户名前缀判断部门
	// 用户名格式: dp{departmentID}_{randomString}
	// 例如: dp1_o849ej5j 属于部门1, dp2_9g5ovd32 属于部门2
	expectedPrefix := "dp" + departmentID + "_"
	return strings.HasPrefix(strings.ToLower(username), strings.ToLower(expectedPrefix))
}

// getRegionFromProxyGroup 从代理组名称推断地区
func getRegionFromProxyGroup(proxyGroup string) string {
	proxyGroup = strings.ToUpper(proxyGroup)

	// 根据代理组名称推断地区
	//if strings.Contains(proxyGroup, "US") || strings.Contains(proxyGroup, "AMERICA") || strings.Contains(proxyGroup, "UNITED STATES") {
	//	return "美国"
	//} else if strings.Contains(proxyGroup, "HK") || strings.Contains(proxyGroup, "HONGKONG") {
	//	return "香港"
	//} else if strings.Contains(proxyGroup, "JP") || strings.Contains(proxyGroup, "JAPAN") {
	//	return "日本"
	//} else if strings.Contains(proxyGroup, "SG") || strings.Contains(proxyGroup, "SINGAPORE") {
	//	return "新加坡"
	//} else if strings.Contains(proxyGroup, "VIP") {
	//	return "VIP专线"
	//}

	return proxyGroup
}
