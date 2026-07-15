import { abilityAccessCtrl, common, Permissions } from '@kit.AbilityKit'
import { geoLocationManager } from '@kit.LocationKit'
import { camera, cameraPicker } from '@kit.CameraKit'
import web_webview from '@ohos.web.webview'

class TrackPoint {
  lat: number
  lng: number

  constructor(lat: number, lng: number) {
    this.lat = lat
    this.lng = lng
  }
}

@Entry
@Component
struct Index {
  @State account: string = ''
  @State password: string = ''
  @State loginError: string = ''
  @State isLoggedIn: boolean = false

  @State latitude: string = '未获取'
  @State longitude: string = '未获取'
  @State searchKeyword: string = ''
  @State isSatellite: boolean = false

  @State photoUri: string = '未拍照'
  @State photoTime: string = '未记录'

  @State startKeyword: string = ''
  @State endKeyword: string = ''
  @State routeMode: string = 'driving'

  @State activeTab: string = 'home'
  @State panelLevel: number = 1 // 0=收起 1=半展开 2=全展开
  @State isRealtimeMode: boolean = false

  private webController: web_webview.WebviewController = new web_webview.WebviewController()
  private trackPoints: Array<TrackPoint> = []
  private realtimeTimer: number = -1

  private readonly DEMO_ACCOUNT: string = '15541547005'
  private readonly DEMO_PASSWORD: string = 'qwe20050308'

  aboutToDisappear() {
    this.stopRealtimeMode(false)
  }

  private getPanelHeight(): number {
    if (this.panelLevel === 0) {
      return 120
    }
    if (this.panelLevel === 1) {
      return 390
    }
    return 680
  }

  private async requestBasicPermissions() {
    let context = getContext(this) as common.UIAbilityContext
    let atManager = abilityAccessCtrl.createAtManager()

    let permissions: Permissions[] = [
      'ohos.permission.APPROXIMATELY_LOCATION',
      'ohos.permission.LOCATION',
      'ohos.permission.CAMERA'
    ]

    return await atManager.requestPermissionsFromUser(context, permissions)
  }

  private async getCurrentPosition(silent: boolean = false): Promise<boolean> {
    try {
      let permissionResult = await this.requestBasicPermissions()

      if (!permissionResult || !permissionResult.authResults || permissionResult.authResults.length < 2) {
        if (!silent) {
          this.showToast('权限申请结果异常')
        }
        return false
      }

      let approxGranted = permissionResult.authResults[0] === 0
      let preciseGranted = permissionResult.authResults[1] === 0

      if (!approxGranted || !preciseGranted) {
        if (!silent) {
          this.showToast('定位权限被拒绝，请在系统设置中开启')
        }
        return false
      }

      const request: geoLocationManager.SingleLocationRequest = {
        locatingPriority: geoLocationManager.LocatingPriority.PRIORITY_LOCATING_SPEED,
        locatingTimeoutMs: 10000
      }

      const location = await geoLocationManager.getCurrentLocation(request)
      this.latitude = String(location.latitude)
      this.longitude = String(location.longitude)

      this.pushGnssObservationToWeb(Number(this.longitude), Number(this.latitude))

      if (!silent) {
        this.showToast('定位成功')
      }
      return true
    } catch (error) {
      if (!silent) {
        this.showToast(`定位失败：${JSON.stringify(error)}`)
      }
      return false
    }
  }

  private pushGnssObservationToWeb(lng: number, lat: number) {
    this.runMapJs(`window.pushGnssObservation && window.pushGnssObservation(${lng}, ${lat}, ${Date.now()});`)
    this.runMapJs(`window.refreshGnssRealtimePanels && window.refreshGnssRealtimePanels();`)
  }

  private async pollLatestLocationOnce(pushToMap: boolean = true, silent: boolean = true) {
    let ok = await this.getCurrentPosition(silent)
    if (!ok) {
      return
    }

    const lat = Number(this.latitude)
    const lng = Number(this.longitude)

    if (pushToMap) {
      this.runMapJs(`showCurrentLocationFromWGS84(${lng}, ${lat});`)
    }

    if (this.trackPoints.length === 0) {
      this.trackPoints.push(new TrackPoint(lat, lng))
    } else {
      const last = this.trackPoints[this.trackPoints.length - 1]
      if (Math.abs(last.lat - lat) > 1e-9 || Math.abs(last.lng - lng) > 1e-9) {
        this.trackPoints.push(new TrackPoint(lat, lng))
      }
    }

    if (this.isRealtimeMode && this.trackPoints.length > 1) {
      let pointsJs = '[' + this.trackPoints.map(item => `[${item.lng}, ${item.lat}]`).join(',') + ']'
      this.runMapJs(`drawTrackFromWGS84(${pointsJs});`)
    }

    this.runMapJs(`window.refreshGnssRealtimePanels && window.refreshGnssRealtimePanels();`)
  }

  private startRealtimeMode() {
    if (this.isRealtimeMode) {
      return
    }

    this.isRealtimeMode = true
    this.showToast('实时动态模式已开启')
    this.pollLatestLocationOnce(true, true)

    this.realtimeTimer = setInterval(() => {
      this.pollLatestLocationOnce(true, true)
    }, 2000) as number
  }

  private stopRealtimeMode(showMsg: boolean = true) {
    if (!this.isRealtimeMode && this.realtimeTimer === -1) {
      return
    }

    this.isRealtimeMode = false

    if (this.realtimeTimer !== -1) {
      clearInterval(this.realtimeTimer)
      this.realtimeTimer = -1
    }

    if (showMsg) {
      this.showToast('实时动态模式已关闭')
    }
  }

  private toggleRealtimeMode() {
    if (this.isRealtimeMode) {
      this.stopRealtimeMode(true)
    } else {
      this.startRealtimeMode()
    }
  }

  private doLogin() {
    if (this.account === this.DEMO_ACCOUNT && this.password === this.DEMO_PASSWORD) {
      this.loginError = ''
      this.isLoggedIn = true
      return
    }
    this.loginError = '账号或密码错误'
  }

  private showToast(msg: string) {
    this.runMapJs(`showAppToast('${msg.replace(/'/g, "\\'")}');`)
  }

  private runMapJs(jsCode: string) {
    try {
      this.webController.runJavaScript(jsCode)
    } catch (error) {
      console.error(`地图脚本执行失败：${JSON.stringify(error)}`)
    }
  }

  private async locateCurrentOnMap() {
    let ok = await this.getCurrentPosition(false)
    if (!ok) {
      return
    }

    const lat = Number(this.latitude)
    const lng = Number(this.longitude)
    this.runMapJs(`showCurrentLocationFromWGS84(${lng}, ${lat});`)
  }

  private async doSearch() {
    if (!this.searchKeyword.trim()) {
      this.showToast('请输入地点关键字')
      return
    }

    const safeKeyword = this.searchKeyword.replace(/'/g, "\\'")
    this.runMapJs(`searchPlace('${safeKeyword}');`)
  }

  private toggleSatellite() {
    this.isSatellite = !this.isSatellite
    this.runMapJs(`toggleSatellite(${this.isSatellite ? 'true' : 'false'});`)
    this.showToast(this.isSatellite ? '已切换到卫星图' : '已切换到标准图')
  }

  private async addFence() {
    let ok = await this.getCurrentPosition(true)
    if (!ok) {
      this.showToast('围栏添加失败：无法获取当前位置')
      return
    }

    const lat = Number(this.latitude)
    const lng = Number(this.longitude)
    const radius = 200

    this.runMapJs(`drawFenceFromWGS84(${lng}, ${lat}, ${radius});`)
    this.showToast('围栏添加成功')
  }

  private removeFence() {
    this.runMapJs(`removeFence();`)
    this.showToast('围栏已删除')
  }

  private async addTrack() {
    let ok = await this.getCurrentPosition(true)
    if (!ok) {
      this.showToast('轨迹添加失败：无法获取当前位置')
      return
    }

    const lat = Number(this.latitude)
    const lng = Number(this.longitude)
    this.trackPoints.push(new TrackPoint(lat, lng))

    let pointsJs = '[' + this.trackPoints.map(item => `[${item.lng}, ${item.lat}]`).join(',') + ']'
    this.runMapJs(`drawTrackFromWGS84(${pointsJs});`)
    this.showToast(`已添加轨迹点：${this.trackPoints.length} 个`)
  }

  private clearTrack() {
    this.trackPoints = []
    this.runMapJs(`clearTrack();`)
    this.showToast('轨迹已清除')
  }

  private async handlePhotoLocation() {
    try {
      let ok = await this.getCurrentPosition(true)
      if (!ok) {
        this.showToast('拍照定位失败：无法获取当前位置')
        return
      }

      const pickerProfile: cameraPicker.PickerProfile = {
        cameraPosition: camera.CameraPosition.CAMERA_POSITION_BACK
      }

      const pickerResult: cameraPicker.PickerResult = await cameraPicker.pick(
        this.getUIContext().getHostContext(),
        [cameraPicker.PickerMediaType.PHOTO],
        pickerProfile
      )

      if (!pickerResult || !pickerResult.resultUri) {
        this.showToast('用户取消拍照或未返回照片')
        return
      }

      this.photoUri = pickerResult.resultUri
      this.photoTime = new Date().toLocaleString()

      const lat = Number(this.latitude)
      const lng = Number(this.longitude)
      const safeUri = this.photoUri.replace(/'/g, "\\'")

      this.runMapJs(`addPhotoMarkerFromWGS84(${lng}, ${lat}, '${safeUri}');`)
      this.showToast('拍照定位成功')
    } catch (error) {
      this.showToast(`拍照定位失败：${JSON.stringify(error)}`)
    }
  }

  private setRouteMode(mode: string) {
    this.routeMode = mode
  }

  private doNavigate() {
    if (!this.startKeyword.trim() || !this.endKeyword.trim()) {
      this.showToast('请输入起点和终点')
      return
    }

    const safeStart = this.startKeyword.replace(/'/g, "\\'")
    const safeEnd = this.endKeyword.replace(/'/g, "\\'")
    const safeMode = this.routeMode.replace(/'/g, "\\'")
    this.runMapJs(`planRoute('${safeStart}', '${safeEnd}', '${safeMode}');`)
  }

  private clearRoute() {
    this.runMapJs(`clearRoute();`)
    this.showToast('路线已清除')
  }

  private openGnssTool(tool: string) {
    this.activeTab = 'gnss'
    this.panelLevel = 0
    this.runMapJs(`openGnssTool('${tool}');`)
  }

  private async openGnssToolWithCurrent(tool: string) {
    await this.getCurrentPosition(true)
    this.activeTab = 'gnss'
    this.panelLevel = 0
    this.runMapJs(`openGnssTool('${tool}');`)
  }

  private cyclePanelLevel() {
    if (this.panelLevel === 0) {
      this.panelLevel = 1
      return
    }
    if (this.panelLevel === 1) {
      this.panelLevel = 2
      return
    }
    this.panelLevel = 0
  }

  private expandPanel() {
    if (this.panelLevel < 2) {
      this.panelLevel += 1
    }
  }

  private collapsePanel() {
    if (this.panelLevel > 0) {
      this.panelLevel -= 1
    }
  }

  private switchTab(tab: string) {
    this.activeTab = tab
    if (tab !== 'gnss') {
      this.runMapJs(`closeGnssTool();`)
    }
    if (this.panelLevel === 0) {
      this.panelLevel = 1
    }
  }

  @Builder
  TabButton(label: string, value: string) {
    Button(label)
      .layoutWeight(1)
      .height(38)
      .borderRadius(12)
      .backgroundColor(this.activeTab === value ? '#1E80FF' : '#F2F4F7')
      .fontColor(this.activeTab === value ? Color.White : '#344054')
      .onClick(() => {
        this.switchTab(value)
      })
  }

  @Builder
  PrimaryAction(label: string, action: () => void) {
    Button(label)
      .layoutWeight(1)
      .height(46)
      .borderRadius(14)
      .backgroundColor('#1E80FF')
      .fontColor(Color.White)
      .onClick(() => {
        action()
      })
  }

  @Builder
  LightAction(label: string, action: () => void) {
    Button(label)
      .layoutWeight(1)
      .height(42)
      .borderRadius(14)
      .backgroundColor('#EEF4FF')
      .fontColor('#1E80FF')
      .onClick(() => {
        action()
      })
  }

  @Builder
  DangerAction(label: string, action: () => void) {
    Button(label)
      .layoutWeight(1)
      .height(42)
      .borderRadius(14)
      .backgroundColor('#FFF1F0')
      .fontColor('#D4380D')
      .onClick(() => {
        action()
      })
  }

  @Builder
  ToolCard(title: string, desc: string, action: () => void) {
    Column({ space: 8 }) {
      Text(title)
        .fontSize(18)
        .fontWeight(FontWeight.Medium)
        .fontColor('#101828')
        .width('100%')
        .textAlign(TextAlign.Start)

      Text(desc)
        .fontSize(12)
        .fontColor('#667085')
        .width('100%')
        .textAlign(TextAlign.Start)
        .maxLines(2)
    }
    .width('48%')
    .height(88)
    .padding(12)
    .backgroundColor(Color.White)
    .borderRadius(16)
    .shadow({ radius: 10, color: '#11000000', offsetX: 0, offsetY: 4 })
    .onClick(() => {
      action()
    })
  }

  @Builder
  HomeTab() {
    Column({ space: 12 }) {
      Row({ space: 10 }) {
        TextInput({ placeholder: '搜索地点 / POI / 地址', text: this.searchKeyword })
          .layoutWeight(1)
          .height(46)
          .backgroundColor('#F4F6FA')
          .borderRadius(12)
          .onChange((value: string) => {
            this.searchKeyword = value
          })

        Button('搜索')
          .height(46)
          .borderRadius(12)
          .onClick(() => {
            this.doSearch()
          })
      }

      Row({ space: 8 }) {
        this.PrimaryAction('定位当前位置', () => {
          this.locateCurrentOnMap()
        })

        this.PrimaryAction(this.isRealtimeMode ? '关闭实时' : '开启实时', () => {
          this.toggleRealtimeMode()
        })
      }

      Row({ space: 8 }) {
        this.LightAction('拍照定位', () => {
          this.handlePhotoLocation()
        })

        this.LightAction(this.isSatellite ? '标准图' : '卫星图', () => {
          this.toggleSatellite()
        })
      }

      if (this.panelLevel === 2) {
        Column({ space: 10 }) {
          Text('实时状态')
            .fontSize(16)
            .fontWeight(FontWeight.Medium)
            .width('100%')
            .textAlign(TextAlign.Start)

          Row({ space: 8 }) {
            Column({ space: 4 }) {
              Text('经度')
                .fontSize(12)
                .fontColor('#667085')
              Text(this.longitude)
                .fontSize(14)
                .fontWeight(FontWeight.Medium)
            }
            .layoutWeight(1)
            .padding(12)
            .backgroundColor('#F8FAFC')
            .borderRadius(14)

            Column({ space: 4 }) {
              Text('纬度')
                .fontSize(12)
                .fontColor('#667085')
              Text(this.latitude)
                .fontSize(14)
                .fontWeight(FontWeight.Medium)
            }
            .layoutWeight(1)
            .padding(12)
            .backgroundColor('#F8FAFC')
            .borderRadius(14)
          }

          Row({ space: 8 }) {
            Column({ space: 4 }) {
              Text('实时模式')
                .fontSize(12)
                .fontColor('#667085')
              Text(this.isRealtimeMode ? '已开启' : '未开启')
                .fontSize(13)
            }
            .layoutWeight(1)
            .padding(12)
            .backgroundColor('#F8FAFC')
            .borderRadius(14)

            Column({ space: 4 }) {
              Text('照片状态')
                .fontSize(12)
                .fontColor('#667085')
              Text(this.photoUri === '未拍照' ? '未拍照' : '已记录')
                .fontSize(13)
            }
            .layoutWeight(1)
            .padding(12)
            .backgroundColor('#F8FAFC')
            .borderRadius(14)
          }
        }
      }
    }
  }

  @Builder
  NavTab() {
    Column({ space: 12 }) {
      TextInput({ placeholder: '起点', text: this.startKeyword })
        .width('100%')
        .height(44)
        .backgroundColor('#F4F6FA')
        .borderRadius(12)
        .onChange((value: string) => {
          this.startKeyword = value
        })

      TextInput({ placeholder: '终点', text: this.endKeyword })
        .width('100%')
        .height(44)
        .backgroundColor('#F4F6FA')
        .borderRadius(12)
        .onChange((value: string) => {
          this.endKeyword = value
        })

      Row({ space: 8 }) {
        Button('驾车')
          .layoutWeight(1)
          .height(40)
          .borderRadius(12)
          .backgroundColor(this.routeMode === 'driving' ? '#1E80FF' : '#EAF2FF')
          .fontColor(this.routeMode === 'driving' ? Color.White : '#1E80FF')
          .onClick(() => {
            this.setRouteMode('driving')
          })

        Button('骑行')
          .layoutWeight(1)
          .height(40)
          .borderRadius(12)
          .backgroundColor(this.routeMode === 'riding' ? '#1E80FF' : '#EAF2FF')
          .fontColor(this.routeMode === 'riding' ? Color.White : '#1E80FF')
          .onClick(() => {
            this.setRouteMode('riding')
          })

        Button('步行')
          .layoutWeight(1)
          .height(40)
          .borderRadius(12)
          .backgroundColor(this.routeMode === 'walking' ? '#1E80FF' : '#EAF2FF')
          .fontColor(this.routeMode === 'walking' ? Color.White : '#1E80FF')
          .onClick(() => {
            this.setRouteMode('walking')
          })
      }

      Row({ space: 8 }) {
        this.PrimaryAction('开始导航', () => {
          this.doNavigate()
        })

        this.DangerAction('清除路线', () => {
          this.clearRoute()
        })
      }
    }
  }

  @Builder
  GnssTab() {
    Column({ space: 10 }) {
      Row({ space: 10 }) {
        this.ToolCard('坐标转换', 'WGS84 / GCJ02 / BD09 互转', () => {
          this.openGnssTool('transform')
        })
        this.ToolCard('精度评估', '散布、均值误差、RMS、CEP95', () => {
          this.openGnssToolWithCurrent('precision')
        })
      }

      Row({ space: 10 }) {
        this.ToolCard('质量评估', '卫星数、SNR、DOP 解析', () => {
          this.openGnssTool('quality')
        })
        this.ToolCard('误差分析', '多路径、几何、噪声综合分析', () => {
          this.openGnssToolWithCurrent('errors')
        })
      }

      Row({ space: 10 }) {
        this.ToolCard('组合导航', 'GNSS + 惯性平滑实验', () => {
          this.openGnssTool('fusion')
        })
        this.ToolCard('欺骗检测', '位置突跳、速度异常、弱信号检测', () => {
          this.openGnssToolWithCurrent('spoof')
        })
      }

      Row({ space: 10 }) {
        this.ToolCard('CORS / PPP', '差分改正与长时间窗平滑实验', () => {
          this.openGnssTool('correction')
        })
        this.ToolCard('GNSS 总览', '实时刷新所有 GNSS 工具统计', () => {
          this.openGnssTool('overview')
        })
      }
    }
  }

  @Builder
  ToolsTab() {
    Column({ space: 12 }) {
      Row({ space: 8 }) {
        this.PrimaryAction('定位', () => {
          this.locateCurrentOnMap()
        })

        this.PrimaryAction(this.isRealtimeMode ? '关闭实时' : '开启实时', () => {
          this.toggleRealtimeMode()
        })
      }

      Row({ space: 8 }) {
        this.LightAction('添加围栏', () => {
          this.addFence()
        })

        this.DangerAction('删除围栏', () => {
          this.removeFence()
        })

        this.LightAction(this.isSatellite ? '标准图' : '卫星图', () => {
          this.toggleSatellite()
        })
      }

      Row({ space: 8 }) {
        this.LightAction('添加轨迹', () => {
          this.addTrack()
        })

        this.DangerAction('清空轨迹', () => {
          this.clearTrack()
        })
      }

      Row({ space: 8 }) {
        this.LightAction('拍照定位', () => {
          this.handlePhotoLocation()
        })
      }
    }
  }

  @Builder
  PanelContent() {
    if (this.activeTab === 'home') {
      this.HomeTab()
    } else if (this.activeTab === 'nav') {
      this.NavTab()
    } else if (this.activeTab === 'gnss') {
      this.GnssTab()
    } else {
      this.ToolsTab()
    }
  }

  @Builder
  LoginPage() {
    Column({ space: 20 }) {
      Blank().height('10%')

      Text('鸿蒙导航定位APP')
        .fontSize(30)
        .fontWeight(FontWeight.Bold)

      Column({ space: 16 }) {
        TextInput({ placeholder: '请输入账号', text: this.account })
          .width('100%')
          .height(52)
          .type(InputType.PhoneNumber)
          .backgroundColor('#F6F7FB')
          .borderRadius(14)
          .onChange((value: string) => {
            this.account = value
          })

        TextInput({ placeholder: '请输入密码', text: this.password })
          .width('100%')
          .height(52)
          .type(InputType.Password)
          .backgroundColor('#F6F7FB')
          .borderRadius(14)
          .onChange((value: string) => {
            this.password = value
          })

        Button('登录')
          .width('100%')
          .height(52)
          .borderRadius(14)
          .onClick(() => {
            this.doLogin()
          })

        if (this.loginError) {
          Text(this.loginError)
            .fontColor('#E84026')
            .fontSize(14)
        }
      }
      .width('86%')
      .padding(20)
      .backgroundColor(Color.White)
      .borderRadius(20)
      .shadow({ radius: 20, color: '#1A000000', offsetX: 0, offsetY: 8 })

      Text('演示账号：15541547005\n演示密码：qwe20050308')
        .fontSize(13)
        .fontColor('#666666')
        .textAlign(TextAlign.Center)
    }
    .width('100%')
    .height('100%')
    .justifyContent(FlexAlign.Center)
    .backgroundColor('#EEF3FF')
  }

  @Builder
  MainPage() {
    Stack({ alignContent: Alignment.Bottom }) {
      Web({
        src: $rawfile('amap.html'),
        controller: this.webController
      })
        .width('100%')
        .height('100%')

      Column({ space: 12 }) {
        Row() {
          Blank()
            .width(48)
            .height(5)
            .borderRadius(3)
            .backgroundColor('#D0D5DD')
            .onClick(() => {
              this.cyclePanelLevel()
            })
        }
        .justifyContent(FlexAlign.Center)
        .width('100%')
        .margin({ top: 6 })

        Row({ space: 8 }) {
          Button('－')
            .width(44)
            .height(28)
            .borderRadius(10)
            .backgroundColor('#F2F4F7')
            .fontColor('#344054')
            .onClick(() => {
              this.collapsePanel()
            })

          Button(this.panelLevel === 0 ? '已收起' : this.panelLevel === 1 ? '半展开' : '全展开')
            .layoutWeight(1)
            .height(28)
            .borderRadius(10)
            .backgroundColor('#F8FAFC')
            .fontColor('#475467')
            .onClick(() => {
              this.cyclePanelLevel()
            })

          Button('＋')
            .width(44)
            .height(28)
            .borderRadius(10)
            .backgroundColor('#F2F4F7')
            .fontColor('#344054')
            .onClick(() => {
              this.expandPanel()
            })
        }

        Row({ space: 8 }) {
          this.TabButton('首页', 'home')
          this.TabButton('导航', 'nav')
          this.TabButton('GNSS', 'gnss')
          this.TabButton('工具', 'tools')
        }

        if (this.panelLevel === 0) {
          Row({ space: 8 }) {
            TextInput({ placeholder: '搜索地点 / 去哪里', text: this.searchKeyword })
              .layoutWeight(1)
              .height(44)
              .backgroundColor('#F4F6FA')
              .borderRadius(12)
              .onChange((value: string) => {
                this.searchKeyword = value
              })

            Button('搜索')
              .height(44)
              .borderRadius(12)
              .onClick(() => {
                this.doSearch()
              })
          }
        } else {
          Scroll() {
            Column({ space: 14 }) {
              this.PanelContent()
            }
            .width('100%')
          }
          .width('100%')
          .layoutWeight(1)
          .scrollBar(BarState.Off)
        }
      }
      .width('100%')
      .height(this.getPanelHeight())
      .padding({ left: 16, right: 16, top: 8, bottom: 20 })
      .backgroundColor(Color.White)
      .borderRadius({ topLeft: 28, topRight: 28 })
      .shadow({ radius: 18, color: '#22000000', offsetX: 0, offsetY: -4 })
    }
    .width('100%')
    .height('100%')
  }

  build() {
    if (!this.isLoggedIn) {
      this.LoginPage()
    } else {
      this.MainPage()
    }
  }
}
