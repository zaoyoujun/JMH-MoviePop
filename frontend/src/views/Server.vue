<template>
  <main class="server-page">
    <header class="server-header">
      <div>
        <h1>服务器</h1>
        <p>集中管理 WebDAV、OpenList 与本地媒体源，查看每个资源库的匹配情况。</p>
      </div>
      <div class="header-actions">
        <n-button type="primary" size="large" class="add-button" @click="showTypePicker = !showTypePicker">
          <template #icon>
            <n-icon><AddOutline /></n-icon>
          </template>
          添加数据源
        </n-button>

        <div v-if="showTypePicker" class="type-picker">
          <h2>选择服务器类型：</h2>
          <div class="type-options">
            <button
              v-for="option in sourceOptions"
              :key="option.value"
              type="button"
              @click="openSourceForm(option)"
            >
              <span v-if="option.badge" class="option-badge">{{ option.badge }}</span>
              {{ option.label }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <section class="library-section">
      <h2>资源库</h2>

      <div class="source-grid">
        <article
          v-for="source in sources"
          :key="source.id"
          class="source-card"
          :class="{ active: source.active }"
          :style="{ '--card-tint': source.tint }"
        >
          <button class="card-menu-button" type="button" @click="toggleMenu(source.id)">
            <n-icon><OptionsOutline /></n-icon>
          </button>

          <div v-if="openedMenu === source.id" class="card-menu">
            <button type="button" @click="openEditModal(source)">
              <n-icon><CreateOutline /></n-icon>
              修改
            </button>
            <button type="button" @click="handleRescan(source.id)">
              <n-icon><RefreshOutline /></n-icon>
              重扫
            </button>
            <button type="button" class="danger" @click="handleDelete(source.id)">
              <n-icon><TrashOutline /></n-icon>
              删除
            </button>
          </div>

          <div class="source-main">
            <strong>{{ source.name }}</strong>
            <span>{{ source.type }}</span>
          </div>

          <div class="source-stats">
            <span><b>{{ source.files }}</b> 文件</span>
            <span><b>{{ source.movies }}</b> 电影</span>
            <span><b>{{ source.series }}</b> 剧集</span>
            <span><b>{{ source.anime }}</b> 动漫</span>
            <span><b>{{ source.music }}</b> 音乐</span>
          </div>

          <p class="unmatched">未匹配 {{ source.unmatched }}</p>

          <div class="poster-strip">
            <i v-for="index in 5" :key="index"></i>
          </div>

          <p class="source-path">{{ decodeSourcePath(source.path) }}</p>
        </article>
      </div>
    </section>

    <n-modal v-model:show="showAddModal" preset="card" class="source-modal">
      <div class="modal-header">
        <h3>{{ sourceForm.type === 'openlist' ? '添加内置OpenList' : '添加 ' + sourceForm.type }}</h3>
        <button class="close-btn" @click="showAddModal = false">返回</button>
      </div>
      <div class="modal-content">
        <div class="form-item">
          <label>名称</label>
          <input v-model="sourceForm.name" type="text" placeholder="如：坚果云" />
        </div>
        
        <!-- 内置OpenList专属字段 -->
        <template v-if="sourceForm.type === 'openlist'">
          <div class="form-item">
            <label>选择存储驱动</label>
            <select v-model="sourceForm.driver" class="driver-select">
              <option value="" disabled>请选择存储驱动</option>
              <option value="quark">夸克网盘</option>
              <option value="baidu">百度网盘</option>
            </select>
          </div>
          <template v-if="sourceForm.driver">
            <div class="form-item">
              <label>Cookie</label>
              <input v-model="sourceForm.cookie" type="text" :placeholder="sourceForm.driver === 'quark' ? '请输入夸克网盘Cookie' : '请输入百度网盘Cookie'" />
            </div>
            <div class="form-item">
              <label>默认挂载路径</label>
              <input v-model="sourceForm.mountPath" type="text" :placeholder="sourceForm.driver === 'quark' ? '/quark' : '/baidu'" />
            </div>
          </template>
        </template>
        
        <!-- WebDAV专属字段 -->
        <template v-else-if="sourceForm.type === 'WebDAV'">
          <div class="form-item-row">
            <div class="form-item flex-1">
              <label>主机</label>
              <input v-model="sourceForm.host" type="text" placeholder="dav.example.com" />
            </div>
            <div class="form-item port-item">
              <label>端口</label>
              <input v-model="sourceForm.port" type="text" placeholder="选填" />
            </div>
          </div>
          <div class="form-item">
            <label>协议</label>
            <div class="protocol-buttons">
              <button 
                class="protocol-btn" 
                :class="{ active: sourceForm.protocol === 'http' }"
                @click="sourceForm.protocol = 'http'"
              >
                HTTP
              </button>
              <button 
                class="protocol-btn" 
                :class="{ active: sourceForm.protocol === 'https' }"
                @click="sourceForm.protocol = 'https'"
              >
                HTTPS
              </button>
            </div>
          </div>
          <div class="form-item">
            <label>用户名</label>
            <input v-model="sourceForm.username" type="text" placeholder="选填" />
          </div>
          <div class="form-item">
            <label>密码</label>
            <input v-model="sourceForm.password" type="password" placeholder="选填" />
          </div>
          <div class="form-item">
            <label>挂载目录</label>
            <div class="mount-paths-container">
              <div v-if="selectedPaths.length === 0" class="no-paths">
                <span class="no-paths-text">暂无挂载目录</span>
              </div>
              <div v-else class="mount-paths-grid">
                <div 
                  v-for="(p, index) in selectedPaths" 
                  :key="index" 
                  class="mount-path-card"
                >
                  <span class="path-icon">📂</span>
                  <span class="path-text">{{ p }}</span>
                  <button class="remove-btn" @click="removeFromSelectedPaths(index)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>
              </div>
              <button class="add-path-btn" @click="browseDirectory()" :disabled="browsing">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 5v14"></path>
                  <path d="M5 12h14"></path>
                </svg>
                {{ browsing ? '浏览中...' : '添加目录' }}
              </button>
            </div>
          </div>
        </template>
        
        <!-- 本地存储专属字段 -->
        <template v-else-if="sourceForm.type === '本地存储'">
          <div class="form-item">
            <label>路径</label>
            <input v-model="sourceForm.path" type="text" placeholder="请输入本地路径" />
          </div>
        </template>
      </div>
      <div class="modal-footer">
        <button class="connect-btn" @click="addSource">连接</button>
        <button class="cancel-btn" @click="showAddModal = false">取消</button>
      </div>
    </n-modal>

    <!-- 编辑数据源弹窗 -->
    <n-modal v-model:show="showEditModal" preset="card" title="修改数据源" style="max-width: 500px;">
      <div class="modal-content">
        <div class="form-item">
          <label>名称</label>
          <input v-model="editForm.name" type="text" placeholder="请输入数据源名称" />
        </div>
        
        <!-- 内置OpenList专属字段 -->
        <template v-if="editForm.type === 'openlist'">
          <div class="form-item">
            <label>选择存储驱动</label>
            <select v-model="editForm.driver" class="driver-select">
              <option value="" disabled>请选择存储驱动</option>
              <option value="quark">夸克网盘</option>
              <option value="baidu">百度网盘</option>
            </select>
          </div>
          <template v-if="editForm.driver">
            <div class="form-item">
              <label>Cookie</label>
              <input v-model="editForm.cookie" type="text" :placeholder="editForm.driver === 'quark' ? '请输入夸克网盘Cookie' : '请输入百度网盘Cookie'" />
            </div>
            <div class="form-item">
              <label>默认挂载路径</label>
              <input v-model="editForm.mountPath" type="text" :placeholder="editForm.driver === 'quark' ? '/quark' : '/baidu'" />
            </div>
          </template>
        </template>
        
        <!-- WebDAV专属字段 -->
        <template v-else-if="editForm.type === 'WebDAV'">
          <div class="form-item-row">
            <div class="form-item flex-1">
              <label>主机</label>
              <input v-model="editForm.host" type="text" placeholder="dav.example.com" />
            </div>
            <div class="form-item port-item">
              <label>端口</label>
              <input v-model="editForm.port" type="text" placeholder="选填" />
            </div>
          </div>
          <div class="form-item">
            <label>协议</label>
            <div class="protocol-buttons">
              <button 
                class="protocol-btn" 
                :class="{ active: editForm.protocol === 'http' }"
                @click="editForm.protocol = 'http'"
              >
                HTTP
              </button>
              <button 
                class="protocol-btn" 
                :class="{ active: editForm.protocol === 'https' }"
                @click="editForm.protocol = 'https'"
              >
                HTTPS
              </button>
            </div>
          </div>
          <div class="form-item">
            <label>用户名</label>
            <input v-model="editForm.username" type="text" placeholder="选填" />
          </div>
          <div class="form-item">
            <label>密码</label>
            <input v-model="editForm.password" type="password" placeholder="选填" />
          </div>
          <div class="form-item">
            <label>挂载目录</label>
            <div class="mount-paths-container">
              <div v-if="editMountPaths.length === 0" class="no-paths">
                <span class="no-paths-text">暂无挂载目录</span>
              </div>
              <div v-else class="mount-paths-grid">
                <div 
                  v-for="(p, index) in editMountPaths" 
                  :key="index" 
                  class="mount-path-card"
                >
                  <span class="path-icon">📂</span>
                  <span class="path-text">{{ p }}</span>
                  <button class="remove-btn" @click="removeEditPath(index)">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </button>
                </div>
              </div>
              <button class="add-path-btn" @click="browseEditDirectory()" :disabled="browsing">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 5v14"></path>
                  <path d="M5 12h14"></path>
                </svg>
                {{ browsing ? '浏览中...' : '添加目录' }}
              </button>
            </div>
          </div>
        </template>
        
        <!-- 本地存储专属字段 -->
        <template v-else-if="editForm.type === '本地存储'">
          <div class="form-item">
            <label>路径</label>
            <input v-model="editForm.path" type="text" placeholder="请输入本地路径" />
          </div>
        </template>
      </div>
      <div class="modal-footer">
        <button class="connect-btn" @click="updateSource">保存</button>
        <button class="cancel-btn" @click="showEditModal = false">取消</button>
      </div>
    </n-modal>

    <!-- 目录浏览弹窗 -->
    <n-modal v-model:show="showBrowseModal" preset="card" title="选择目录" style="max-width: 500px;">
      <div class="browse-modal">
        <div class="browse-header">
          <button class="back-btn" @click="goBack" :disabled="currentPath === '/'">返回</button>
          <span class="current-path">{{ currentPath }}</span>
          <div class="header-right">
            <label class="multi-select-switch">
              <input type="checkbox" v-model="isMultiSelect" />
              <span>多选</span>
            </label>
            <button class="select-dir-btn" @click="selectCurrentDir">选择此目录</button>
          </div>
        </div>
        
        <div v-if="isMultiSelect && selectedPaths.length > 0" class="selected-info">
          已选择 {{ selectedPaths.length }} 个目录
          <button class="clear-btn" @click="clearSelection">清空</button>
        </div>
        
        <div class="browse-list">
          <div v-if="browseItems.length === 0" class="browse-empty">目录为空</div>
          <div
            v-for="item in browseItems"
            :key="item.path"
            class="browse-item"
            :class="{ 'is-dir': item.isDir, 'is-selected': item.isDir && isSelected(item) }"
          >
            <span v-if="isMultiSelect && item.isDir" class="item-checkbox" @click.stop="toggleSelect(item)">
              {{ isSelected(item) ? '✓' : '' }}
            </span>
            <span class="item-icon" @click="item.isDir && browseDirectory(item.path)">{{ item.isDir ? '📁' : '📄' }}</span>
            <span class="item-name" @click="item.isDir && browseDirectory(item.path)">{{ item.name }}</span>
            <button
              v-if="isMultiSelect && item.isDir"
              class="add-subdir-btn"
              @click="browseDirectory(item.path)"
              title="进入子目录"
            >
              进入
            </button>
            <span v-if="!item.isDir && item.size" class="item-size">{{ formatSize(item.size) }}</span>
          </div>
        </div>
        
        <div v-if="isMultiSelect" class="browse-footer">
          <button class="confirm-btn" @click="confirmSelection" :disabled="selectedPaths.length === 0">
            确认选择 ({{ selectedPaths.length }})
          </button>
        </div>
      </div>
    </n-modal>

    <!-- 编辑模态框专用目录浏览弹窗 -->
    <n-modal v-model:show="showEditBrowseModal" preset="card" title="选择挂载目录" style="max-width: 500px;">
      <div class="browse-modal">
        <div class="browse-header">
          <button class="back-btn" @click="goBack" :disabled="currentPath === '/'">返回</button>
          <span class="current-path">{{ currentPath }}</span>
          <button class="select-dir-btn" @click="addEditPath(currentPath); showEditBrowseModal = false">添加此目录</button>
        </div>
        <div class="browse-list">
          <div v-if="browseItems.length === 0" class="browse-empty">目录为空</div>
          <div
            v-for="item in browseItems"
            :key="item.path"
            class="browse-item"
            :class="{ 'is-dir': item.isDir, 'is-selected': item.isDir && editMountPaths.includes(item.path) }"
          >
            <span v-if="item.isDir" class="item-checkbox" @click.stop="handleEditBrowseClick(item)">
              {{ editMountPaths.includes(item.path) ? '✓' : '' }}
            </span>
            <span class="item-icon" @click="item.isDir && browseDirectory(item.path)">{{ item.isDir ? '📁' : '📄' }}</span>
            <span class="item-name" @click="item.isDir && browseDirectory(item.path)">{{ item.name }}</span>
            <button
              v-if="item.isDir"
              class="add-subdir-btn"
              @click="browseDirectory(item.path)"
              title="进入子目录"
            >
              进入
            </button>
            <span v-if="!item.isDir && item.size" class="item-size">{{ formatSize(item.size) }}</span>
          </div>
        </div>
      </div>
    </n-modal>
  </main>
</template>

<script setup>
import { computed, reactive, ref, watch, onMounted } from 'vue'
import {
  AddOutline,
  CreateOutline,
  OptionsOutline,
  RefreshOutline,
  TrashOutline
} from '@vicons/ionicons5'

// API基础地址
const API_BASE = 'http://localhost:8000'

const openedMenu = ref('')
const showTypePicker = ref(false)
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingSourceId = ref('')
const verifying = ref(false)
const verifyStatus = ref(null)
const browsing = ref(false)
const browseItems = ref([])
const currentPath = ref('/')
const showBrowseModal = ref(false)
const selectedPaths = ref([])
const isMultiSelect = ref(true)

const sources = ref([])

// 加载数据源列表
async function loadSources() {
  try {
    const response = await fetch(`${API_BASE}/api/sources`)
    const data = await response.json()
    if (data.code === 0) {
      sources.value = data.data || []
    }
  } catch (error) {
    console.error('加载数据源失败:', error)
  }
}

// 验证 WebDAV 连接
async function verifyWebDAVConnection() {
  if (!sourceForm.host.trim()) {
    alert('请输入主机地址')
    return false
  }

  verifying.value = true
  const params = new URLSearchParams()
  params.append('host', sourceForm.host.trim())
  params.append('port', sourceForm.port || '')
  params.append('protocol', sourceForm.protocol)
  params.append('username', sourceForm.username || '')
  params.append('password', sourceForm.password || '')
  // 使用根路径验证连接，不使用用户选择的路径
  params.append('path', '/')

  try {
    const response = await fetch(`${API_BASE}/api/sources/browse`, {
      method: 'POST',
      body: params
    })
    const data = await response.json()

    verifying.value = false
    if (data.code === 0) {
      return true
    } else {
      alert(`连接失败: ${data.message}`)
      return false
    }
  } catch (error) {
    verifying.value = false
    console.error('验证连接失败:', error)
    alert('连接失败，请检查网络和服务器地址')
    return false
  }
}

// 添加数据源
async function addSource() {
  if (!canSubmitSource.value) {
    alert(submitError.value || '请填写必填字段')
    return
  }

  // WebDAV 添加前先验证连接
  if (sourceForm.type === 'WebDAV') {
    const verified = await verifyWebDAVConnection()
    if (!verified) return
  }

  const params = new URLSearchParams()
  params.append('name', sourceForm.name.trim())
  params.append('type', sourceForm.type)
  
  if (sourceForm.type === 'openlist') {
    params.append('driver', sourceForm.driver)
    params.append('cookie', sourceForm.cookie)
    params.append('mount_path', sourceForm.mountPath)
  } else if (sourceForm.type === 'WebDAV') {
    const port = sourceForm.port ? `:${sourceForm.port}` : ''
    // 确保路径以/开头
    const path = sourceForm.path.startsWith('/') ? sourceForm.path : '/' + sourceForm.path
    params.append('path', `${sourceForm.protocol}://${sourceForm.host}${port}${path}`)
    params.append('username', sourceForm.username)
    params.append('password', sourceForm.password)
  } else {
    params.append('path', sourceForm.path)
  }

  try {
    const response = await fetch(`${API_BASE}/api/sources`, {
      method: 'POST',
      body: params
    })
    const data = await response.json()
    if (data.code === 0) {
      await loadSources()
      showAddModal.value = false
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('添加数据源失败:', error)
    alert('添加失败')
  }
}

// 删除数据源
async function removeSource(id) {
  if (!confirm('确定要删除这个数据源吗？')) return
  
  try {
    const response = await fetch(`${API_BASE}/api/sources/${id}`, {
      method: 'DELETE'
    })
    const data = await response.json()
    if (data.code === 0) {
      await loadSources()
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('删除数据源失败:', error)
  }
}

// 验证连接
async function verifyConnection() {
  if (!sourceForm.path.trim() && !sourceForm.host.trim() && !sourceForm.driver) return
  
  verifying.value = true
  verifyStatus.value = null

  try {
    const sourceData = {
      type: sourceForm.type,
      host: sourceForm.host,
      path: sourceForm.path,
      driver: sourceForm.driver
    }
    
    const response = await fetch(`${API_BASE}/api/sources/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(sourceData)
    })
    const data = await response.json()
    
    verifying.value = false
    if (data.code === 0) {
      verifyStatus.value = { type: 'success', text: data.message }
    } else {
      verifyStatus.value = { type: 'error', text: data.message }
    }
  } catch (error) {
    verifying.value = false
    verifyStatus.value = { type: 'error', text: '连接失败' }
  }
}

// 重扫数据源
async function rescanSource(id) {
  try {
    const response = await fetch(`${API_BASE}/api/sources/${id}/rescan`, {
      method: 'POST'
    })
    const data = await response.json()
    if (data.code === 0) {
      alert(data.message)
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('重扫失败:', error)
  }
}

// 初始化加载
onMounted(() => {
  loadSources()
})

const sourceForm = reactive({
  name: '',
  type: '',
  host: '',
  port: '',
  protocol: 'http',
  username: '',
  password: '',
  path: '',
  driver: '',
  cookie: '',
  mountPath: ''
})

watch(() => sourceForm.driver, (newDriver) => {
  if (newDriver === 'quark') {
    sourceForm.mountPath = '/quark'
  } else if (newDriver === 'baidu') {
    sourceForm.mountPath = '/baidu'
  } else {
    sourceForm.mountPath = ''
  }
})

// 浏览目录
async function browseDirectory(path = '/') {
  if (!sourceForm.host.trim()) {
    alert('请先输入主机地址')
    return
  }
  
  browsing.value = true
  currentPath.value = path
  
  const params = new URLSearchParams()
  params.append('host', sourceForm.host.trim())
  params.append('port', sourceForm.port || '')
  params.append('protocol', sourceForm.protocol)
  params.append('username', sourceForm.username || '')
  params.append('password', sourceForm.password || '')
  params.append('path', path)
  
  try {
    const response = await fetch(`${API_BASE}/api/sources/browse`, {
      method: 'POST',
      body: params
    })
    const data = await response.json()
    
    if (data.code === 0) {
      // 对返回的路径进行URL解码
      browseItems.value = (data.data.items || []).map(item => ({
        ...item,
        path: decodeURIComponent(item.path),
        name: decodeURIComponent(item.name)
      }))
      showBrowseModal.value = true
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('浏览目录失败:', error)
    alert('浏览目录失败')
  } finally {
    browsing.value = false
  }
}

// 切换选择状态
function toggleSelect(item) {
  if (!item.isDir) return
  
  const index = selectedPaths.value.indexOf(item.path)
  if (index > -1) {
    selectedPaths.value.splice(index, 1)
  } else {
    selectedPaths.value.push(item.path)
  }
}

// 检查是否已选择
function isSelected(item) {
  return selectedPaths.value.includes(item.path)
}

// 选择目录
function selectPath(item) {
  if (item.isDir) {
    if (isMultiSelect.value) {
      toggleSelect(item)
    } else {
      browseDirectory(item.path)
    }
  } else {
    const parts = item.path.split('/')
    parts.pop()
    const dirPath = parts.join('/') || '/'
    
    if (isMultiSelect.value) {
      const index = selectedPaths.value.indexOf(dirPath)
      if (index === -1) {
        selectedPaths.value.push(dirPath)
      }
    } else {
      sourceForm.path = dirPath
      showBrowseModal.value = false
    }
  }
}

// 返回上级目录
function goBack() {
  if (currentPath.value === '/') return
  const parts = currentPath.value.split('/')
  parts.pop()
  browseDirectory(parts.join('/') || '/')
}

// 选择当前目录
function selectCurrentDir() {
  if (isMultiSelect.value) {
    toggleSelect({ path: currentPath.value, isDir: true })
  } else {
    sourceForm.path = currentPath.value
    showBrowseModal.value = false
  }
}

// 确认选择
function confirmSelection() {
  if (selectedPaths.value.length > 0) {
    // URL编码路径后保存
    sourceForm.path = selectedPaths.value.map(p => encodeURIComponent(p)).join(',')
  }
  showBrowseModal.value = false
}

// 清空选择
function clearSelection() {
  selectedPaths.value = []
}

// 从选择列表中移除路径
function removeFromSelectedPaths(index) {
  selectedPaths.value.splice(index, 1)
}

// 格式化文件大小
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(1) + ' GB'
}

// 解码数据源路径用于显示
function decodeSourcePath(path) {
  if (!path) return ''
  try {
    const url = new URL(path)
    return url.protocol + '://' + url.host + decodeURIComponent(url.pathname)
  } catch {
    return decodeURIComponent(path)
  }
}

const sourceOptions = [
  { label: '内置OpenList', value: 'openlist' },
  { label: 'WebDAV', value: 'WebDAV' },
  { label: '本地目录', value: '本地存储' },
  { label: '待开发', value: 'developing' }
]

const tintOptions = [
  'rgba(111, 110, 142, 0.62)',
  'rgba(95, 30, 30, 0.68)',
  'rgba(45, 83, 102, 0.66)',
  'rgba(91, 47, 116, 0.68)',
  'rgba(39, 98, 82, 0.66)',
  'rgba(101, 74, 38, 0.68)'
]

const canSubmitSource = computed(() => {
  if (!sourceForm.name.trim()) return false
  if (sourceForm.type === 'openlist') return sourceForm.driver && sourceForm.cookie.trim() && sourceForm.mountPath.trim()
  if (sourceForm.type === 'WebDAV') return sourceForm.host.trim() && selectedPaths.value.length > 0
  if (sourceForm.type === '本地存储') return sourceForm.path.trim()
  return true
})

// 获取提交错误信息
const submitError = computed(() => {
  if (!sourceForm.name.trim()) return '请输入数据源名称'
  if (sourceForm.type === 'WebDAV' && !sourceForm.host.trim()) return '请输入主机地址'
  if (sourceForm.type === 'WebDAV' && selectedPaths.value.length === 0) return '请选择挂载目录'
  if (sourceForm.type === '本地存储' && !sourceForm.path.trim()) return '请输入本地路径'
  return ''
})

function toggleMenu(id) {
  openedMenu.value = openedMenu.value === id ? '' : id
}

function openSourceForm(option) {
  if (option.value === 'developing') return
  
  sourceForm.name = option.label
  sourceForm.type = option.value
  sourceForm.host = ''
  sourceForm.port = ''
  sourceForm.protocol = 'http'
  sourceForm.username = ''
  sourceForm.password = ''
  sourceForm.path = ''
  sourceForm.driver = 'local'
  sourceForm.cookie = ''
  sourceForm.mountPath = '/openlist'
  verifyStatus.value = null
  showTypePicker.value = false
  showAddModal.value = true
}

// 编辑表单
const editForm = reactive({
  name: '',
  type: '',
  host: '',
  port: '',
  protocol: 'http',
  username: '',
  password: '',
  path: '',
  driver: '',
  cookie: '',
  mountPath: ''
})

// 编辑模态框的挂载路径列表
const editMountPaths = ref([])
const showEditBrowseModal = ref(false)

// 打开修改模态框
async function openEditModal(source) {
  editingSourceId.value = source.id
  editForm.name = source.name
  editForm.type = source.type
  editForm.driver = source.driver || ''
  editForm.cookie = source.cookie || ''
  editForm.mountPath = source.mount_path || ''
  editForm.username = source.username || ''
  editForm.password = source.password || ''

  if (source.type === 'WebDAV') {
    try {
      const url = new URL(source.path)
      editForm.host = url.hostname
      editForm.port = url.port
      editForm.protocol = url.protocol.replace(':', '')
      // 解码路径
      const decodedPathname = decodeURIComponent(url.pathname || '/')
      // 解析已有的挂载路径列表
      editMountPaths.value = decodedPathname.split(',').filter(p => p.trim())
      // 重新编码路径用于保存（保持与addEditPath一致）
      editForm.path = editMountPaths.value.map(p => encodeURIComponent(p)).join(',')
    } catch (error) {
      console.error('解析URL失败:', error, '原始URL:', source.path)
      // URL解析失败时，尝试从source对象中提取信息
      // 尝试手动解析协议、主机、端口（允许路径部分缺少前导/）
      const pathMatch = source.path.match(/^(https?):\/\/([^\/:]+)(?::(\d+))?(\/?.*)$/)
      if (pathMatch) {
        editForm.protocol = pathMatch[1]
        editForm.host = pathMatch[2]
        editForm.port = pathMatch[3] || ''
        let pathPart = pathMatch[4] || '/'
        // 确保路径以/开头
        if (!pathPart.startsWith('/')) {
          pathPart = '/' + pathPart
        }
        const decodedPath = decodeURIComponent(pathPart)
        // 解析已有的挂载路径列表
        editMountPaths.value = decodedPath.split(',').filter(p => p.trim())
        // 重新编码路径用于保存
        editForm.path = editMountPaths.value.map(p => encodeURIComponent(p)).join(',')
      } else {
        // 完全无法解析，尝试从source对象直接获取字段
        console.error('正则匹配也失败，尝试直接使用source字段')
        editForm.host = source.host || ''
        editForm.port = source.port || ''
        editForm.protocol = source.protocol || 'http'
        const decodedPath = decodeURIComponent(source.path) || '/'
        editMountPaths.value = decodedPath.split(',').filter(p => p.trim())
        editForm.path = editMountPaths.value.map(p => encodeURIComponent(p)).join(',')
      }
    }
  } else {
    editForm.path = source.path || ''
    editMountPaths.value = []
  }

  showEditModal.value = true
  openedMenu.value = ''
}

// 编辑模态框浏览目录
async function browseEditDirectory() {
  if (!editForm.host.trim()) {
    alert('请先输入主机地址')
    return
  }
  
  browsing.value = true
  currentPath.value = '/'
  
  const params = new URLSearchParams()
  params.append('host', editForm.host.trim())
  params.append('port', editForm.port || '')
  params.append('protocol', editForm.protocol)
  params.append('username', editForm.username || '')
  params.append('password', editForm.password || '')
  params.append('path', '/')
  
  try {
    const response = await fetch(`${API_BASE}/api/sources/browse`, {
      method: 'POST',
      body: params
    })
    const data = await response.json()
    
    if (data.code === 0) {
      // 对返回的路径进行URL解码
      browseItems.value = (data.data.items || []).map(item => ({
        ...item,
        path: decodeURIComponent(item.path),
        name: decodeURIComponent(item.name)
      }))
      showEditBrowseModal.value = true
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('浏览目录失败:', error)
    alert('浏览目录失败')
  } finally {
    browsing.value = false
  }
}

// 添加路径到编辑表单
function addEditPath(path) {
  if (!editMountPaths.value.includes(path)) {
    editMountPaths.value.push(path)
    // URL编码路径后保存
    editForm.path = editMountPaths.value.map(p => encodeURIComponent(p)).join(',')
  }
}

// 移除路径
function removeEditPath(index) {
  editMountPaths.value.splice(index, 1)
  // URL编码路径后保存
  editForm.path = editMountPaths.value.map(p => encodeURIComponent(p)).join(',')
}

// 处理编辑模态框目录点击
function handleEditBrowseClick(item) {
  if (item.isDir) {
    addEditPath(item.path)
    showEditBrowseModal.value = false
  }
}

// 更新数据源
async function updateSource() {
  if (!editForm.name.trim()) {
    alert('请输入数据源名称')
    return
  }

  const params = new URLSearchParams()
  params.append('name', editForm.name.trim())
  
  if (editForm.type === 'openlist') {
    if (editForm.driver) params.append('driver', editForm.driver)
    if (editForm.cookie) params.append('cookie', editForm.cookie)
    if (editForm.mountPath) params.append('mount_path', editForm.mountPath)
  } else if (editForm.type === 'WebDAV') {
    const port = editForm.port ? `:${editForm.port}` : ''
    // 确保路径以/开头
    const path = editForm.path.startsWith('/') ? editForm.path : '/' + editForm.path
    params.append('path', `${editForm.protocol}://${editForm.host}${port}${path}`)
    if (editForm.username) params.append('username', editForm.username)
    if (editForm.password) params.append('password', editForm.password)
  } else {
    params.append('path', editForm.path)
    if (editForm.username) params.append('username', editForm.username)
    if (editForm.password) params.append('password', editForm.password)
  }

  try {
    const response = await fetch(`${API_BASE}/api/sources/${editingSourceId.value}`, {
      method: 'PUT',
      body: params
    })
    const data = await response.json()
    if (data.code === 0) {
      await loadSources()
      showEditModal.value = false
    } else {
      alert(data.message)
    }
  } catch (error) {
    console.error('更新数据源失败:', error)
    alert('更新失败')
  }
}

// 处理重扫
async function handleRescan(id) {
  await rescanSource(id)
  openedMenu.value = ''
}

// 处理删除
async function handleDelete(id) {
  await removeSource(id)
  openedMenu.value = ''
}

</script>

<style scoped>
.server-page {
  width: 100%;
  min-height: 100vh;
  height: 100%;
  max-width: 100%;
  padding: 34px;
  box-sizing: border-box;
  color: #f7f9ff;
  background: #1b1b1c;
  position: relative;
  overflow: auto;
}

.server-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 30px;
}

.server-header h1 {
  margin: 0;
  color: #ffffff;
  font-size: 30px;
  line-height: 1.2;
}

.server-header p {
  margin: 8px 0 0;
  color: #8f96a4;
}

.add-button {
  min-width: 136px;
  background: #2f6df6;
}

.header-actions {
  position: relative;
  z-index: 10;
  flex: 0 0 auto;
}

:global(.source-modal) {
  width: min(420px, calc(100vw - 48px)) !important;
}

:global(.source-modal .n-card-header) {
  padding: 18px 20px 8px;
}

:global(.source-modal .n-card__content) {
  padding: 12px 20px 4px;
}

:global(.source-modal .n-card__footer) {
  padding: 12px 20px 18px;
}

.library-section h2 {
  margin: 0 0 18px;
  color: #ffffff;
  font-size: 26px;
}

.type-picker {
  position: absolute;
  top: calc(100% + 12px);
  right: 0;
  z-index: 12;
  width: 312px;
  padding: 12px 8px 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  background: #2b2b2d;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.24);
}

.type-picker h2 {
  margin: 0 8px 8px;
  color: #ffffff;
  font-size: 18px;
}

.type-groups {
  display: grid;
  gap: 4px;
}

.type-group-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 36px;
  padding: 0 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 6px;
  color: #ffffff;
  background: #3c3c3d;
  cursor: pointer;
}

.type-group-head span {
  font-weight: 700;
}

.type-options {
  display: grid;
  gap: 6px;
  padding: 8px 8px 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-top: 0;
  border-radius: 0 0 6px 6px;
  background: #373738;
}

.type-options button {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 32px;
  padding: 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 6px;
  color: #ffffff;
  background: #4a4a4a;
  cursor: pointer;
}

.type-options button:hover {
  border-color: rgba(105, 240, 198, 0.76);
  background: #545454;
}

.option-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 18px;
  padding: 0 5px;
  border-radius: 5px;
  color: #ffffff;
  font-size: 11px;
  font-weight: 800;
  background: #ff784a;
}

.source-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  max-width: 1180px;
}

.source-card {
  position: relative;
  min-height: 194px;
  padding: 18px 16px;
  overflow: visible;
  border: 1px solid transparent;
  border-radius: 8px;
  background:
    linear-gradient(135deg, var(--card-tint), color-mix(in srgb, var(--card-tint) 52%, #171719));
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.2);
}

.source-card.active {
  border-color: #2f6df6;
  box-shadow: 0 0 0 1px rgba(47, 109, 246, 0.28), 0 18px 42px rgba(0, 0, 0, 0.26);
}

.card-menu-button {
  position: absolute;
  top: 16px;
  right: 16px;
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 6px;
  color: #ffffff;
  background: rgba(255, 255, 255, 0.13);
  cursor: pointer;
}

.card-menu {
  position: absolute;
  z-index: 5;
  top: 44px;
  right: 12px;
  width: 152px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  background: #0f1017;
  box-shadow: 0 18px 44px rgba(0, 0, 0, 0.34);
}

.card-menu button {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  height: 38px;
  padding: 0 14px;
  border: 0;
  color: #f4f6fb;
  background: transparent;
  cursor: pointer;
}

.card-menu button:hover {
  background: rgba(255, 255, 255, 0.07);
}

.card-menu .danger {
  color: #ff5757;
}

.source-main {
  padding-right: 40px;
}

.source-main strong {
  display: block;
  color: #ffffff;
  font-size: 17px;
  line-height: 1.2;
}

.source-main span,
.source-path,
.unmatched {
  color: rgba(226, 231, 242, 0.62);
  font-size: 12px;
}

.source-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 14px 0 8px;
  color: #ffffff;
  font-size: 12px;
}

.source-stats b {
  margin-right: 3px;
  color: #ffffff;
}

.unmatched {
  margin: 0 0 16px;
}

.poster-strip {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.poster-strip i {
  display: block;
  height: 56px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.13);
}

.source-path {
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.verify-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: -4px;
}

.verify-status {
  font-size: 13px;
}

.verify-status.success {
  color: #69f0c6;
}

.verify-status.error {
  color: #ff6b6b;
}

/* ===== 新表单样式 ===== */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h3 {
  margin: 0;
  color: #ffffff;
  font-size: 18px;
  font-weight: 600;
}

.modal-header .close-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  background: transparent;
  cursor: pointer;
}

.modal-header .close-btn:hover {
  color: #ffffff;
}

.modal-content {
  padding: 20px;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
}

.form-item input {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.05);
  outline: none;
  box-sizing: border-box;
}

.form-item input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-item input:focus {
  border-color: rgba(47, 109, 246, 0.5);
}

.form-item-row {
  display: flex;
  gap: 12px;
}

.form-item.flex-1 {
  flex: 1;
}

.form-item.port-item {
  flex: 0 0 120px;
}

.protocol-buttons {
  display: flex;
  gap: 8px;
}

.protocol-btn {
  flex: 1;
  height: 40px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
  transition: all 0.2s;
}

.protocol-btn:hover {
  border-color: rgba(47, 109, 246, 0.5);
}

.protocol-btn.active {
  border-color: #2f6df6;
  color: #ffffff;
  background: #2f6df6;
}

.media-path {
  display: flex;
  align-items: center;
  height: 40px;
  padding: 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
}

.media-path .nav-btn,
.media-path .dropdown-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
}

.media-path .nav-btn:hover,
.media-path .dropdown-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.media-path span {
  flex: 1;
  margin: 0 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  text-align: center;
}

.modal-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.connect-btn {
  flex: 1;
  height: 40px;
  border: none;
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  font-weight: 500;
  background: #2f6df6;
  cursor: pointer;
}

.connect-btn:hover {
  background: #3b7dfa;
}

.cancel-btn {
  padding: 0 24px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  background: transparent;
  cursor: pointer;
}

.cancel-btn:hover {
  border-color: rgba(255, 255, 255, 0.3);
}

.driver-select {
  width: 100%;
  height: 40px;
  padding: 0 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #ffffff;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.05);
  outline: none;
  cursor: pointer;
  box-sizing: border-box;
}

.driver-select option {
  color: #000000;
  background: #ffffff;
}

.path-input-row {
  display: flex;
  gap: 8px;
}

.path-input-row input {
  flex: 1;
}

.browse-btn {
  padding: 0 16px;
  border: 1px solid #63e2b7;
  border-radius: 6px;
  color: #63e2b7;
  font-size: 14px;
  background: transparent;
  cursor: pointer;
  white-space: nowrap;
}

.browse-btn:hover:not(:disabled) {
  background: rgba(99, 226, 183, 0.1);
}

.browse-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.browse-modal {
  max-height: 400px;
  display: flex;
  flex-direction: column;
}

.browse-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 12px;
}

.back-btn {
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
  background: transparent;
  cursor: pointer;
}

.back-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.current-path {
  flex: 1;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.select-dir-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  color: #000000;
  font-size: 13px;
  background: #63e2b7;
  cursor: pointer;
}

.browse-list {
  flex: 1;
  overflow-y: auto;
  max-height: 300px;
}

.browse-empty {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  padding: 40px 0;
}

.browse-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.browse-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.browse-item.is-dir {
  cursor: pointer;
}

.item-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.item-name {
  flex: 1;
  color: #ffffff;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-size {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.multi-select-switch {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  cursor: pointer;
}

.multi-select-switch input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.selected-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  margin-bottom: 12px;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  background: rgba(99, 226, 183, 0.1);
}

.clear-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
}

.clear-btn:hover {
  background: rgba(255, 255, 255, 0.15);
}

.item-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  color: #63e2b7;
  font-size: 12px;
  font-weight: bold;
}

.browse-item.is-selected .item-checkbox {
  background: #63e2b7;
  border-color: #63e2b7;
  color: #000000;
}

.browse-item.is-selected {
  background: rgba(99, 226, 183, 0.15);
}

.add-subdir-btn {
  padding: 4px 8px;
  margin-left: auto;
  border: 1px solid rgba(99, 226, 183, 0.5);
  border-radius: 4px;
  color: #63e2b7;
  font-size: 12px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.add-subdir-btn:hover {
  background: rgba(99, 226, 183, 0.1);
  border-color: #63e2b7;
}

.browse-footer {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.confirm-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  color: #000000;
  font-size: 14px;
  font-weight: 500;
  background: #63e2b7;
  cursor: pointer;
}

.confirm-btn:hover:not(:disabled) {
  background: #7fe7c4;
}

.confirm-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.mount-paths-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.no-paths {
  padding: 20px;
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  text-align: center;
}

.no-paths-text {
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
}

.mount-paths-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.mount-path-card {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
}

.mount-path-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

.path-icon {
  font-size: 16px;
}

.path-text {
  flex: 1;
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.remove-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.5);
  background: rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s;
}

.remove-btn:hover {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.15);
}

.add-path-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border: 1px dashed rgba(99, 226, 183, 0.5);
  border-radius: 8px;
  color: #63e2b7;
  font-size: 14px;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.add-path-btn:hover:not(:disabled) {
  border-color: #63e2b7;
  background: rgba(99, 226, 183, 0.1);
}

.add-path-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
