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
  @State routeMode: string = 'driving' // driving / riding / walking

  private webController: web_webview.WebviewController = new web_webview.WebviewController()
  private trackPoints: Array<TrackPoint> = []
  private readonly DEMO_ACCOUNT: string = '15541547005'
  private readonly DEMO_PASSWORD: string = 'qwe20050308'

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

  private async getCurrentPosition(): Promise<boolean> {
    try {
      let permissionResult = await this.requestBasicPermissions()

      if (!permissionResult || !permissionResult.authResults || permissionResult.authResults.length < 2) {
        this.showToast('权限申请结果异常')
        return false
      }

      let approxGranted = permissionResult.authResults[0] === 0
      let preciseGranted = permissionResult.authResults[1] === 0

      if (!approxGranted || !preciseGranted) {
        this.showToast('定位权限被拒绝，请在系统设置中开启')
        return false
      }

      const request: geoLocationManager.SingleLocationRequest = {
        locatingPriority: geoLocationManager.LocatingPriority.PRIORITY_LOCATING_SPEED,
        locatingTimeoutMs: 10000
      }

      const location = await geoLocationManager.getCurrentLocation(request)
      this.latitude = String(location.latitude)
      this.longitude = String(location.longitude)
      this.showToast('定位成功')
      return true
    } catch (error) {
      this.showToast(`定位失败：${JSON.stringify(error)}`)
      return false
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
    let ok = await this.getCurrentPosition()
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
  }

  private async addFence() {
    let ok = await this.getCurrentPosition()
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
    let ok = await this.getCurrentPosition()
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
      let ok = await this.getCurrentPosition()
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

      // 可拖拽底部面板
      Column({ space: 12 }) {
        Row() {
          Blank()
            .width(44)
            .height(5)
            .borderRadius(3)
            .backgroundColor('#D0D5DD')
        }
        .justifyContent(FlexAlign.Center)
        .width('100%')
        .margin({ top: 6 })

        Row({ space: 10 }) {
          TextInput({ placeholder: '搜索某个地点然后定位到那', text: this.searchKeyword })
            .layoutWeight(1)
            .height(46)
            .backgroundColor('#F4F6FA')
            .borderRadius(12)
            .onChange((value: string) => {
              this.searchKeyword = value
            })

          Button('搜索')
            .height(46)
            .onClick(() => {
              this.doSearch()
            })
        }

        Row({ space: 8 }) {
          TextInput({ placeholder: '起点', text: this.startKeyword })
            .layoutWeight(1)
            .height(42)
            .backgroundColor('#F4F6FA')
            .borderRadius(12)
            .onChange((value: string) => {
              this.startKeyword = value
            })

          TextInput({ placeholder: '终点', text: this.endKeyword })
            .layoutWeight(1)
            .height(42)
            .backgroundColor('#F4F6FA')
            .borderRadius(12)
            .onChange((value: string) => {
              this.endKeyword = value
            })
        }

        Row({ space: 8 }) {
          Button('驾车')
            .layoutWeight(1)
            .backgroundColor(this.routeMode === 'driving' ? '#1E80FF' : '#EAF2FF')
            .fontColor(this.routeMode === 'driving' ? Color.White : '#1E80FF')
            .onClick(() => {
              this.setRouteMode('driving')
            })

          Button('骑行')
            .layoutWeight(1)
            .backgroundColor(this.routeMode === 'riding' ? '#1E80FF' : '#EAF2FF')
            .fontColor(this.routeMode === 'riding' ? Color.White : '#1E80FF')
            .onClick(() => {
              this.setRouteMode('riding')
            })

          Button('步行')
            .layoutWeight(1)
            .backgroundColor(this.routeMode === 'walking' ? '#1E80FF' : '#EAF2FF')
            .fontColor(this.routeMode === 'walking' ? Color.White : '#1E80FF')
            .onClick(() => {
              this.setRouteMode('walking')
            })

          Button('导航')
            .layoutWeight(1)
            .onClick(() => {
              this.doNavigate()
            })
        }

        Row({ space: 8 }) {
          Button('定位当前位置')
            .layoutWeight(1)
            .onClick(() => {
              this.locateCurrentOnMap()
            })

          Button('拍照定位')
            .layoutWeight(1)
            .onClick(() => {
              this.handlePhotoLocation()
            })
        }

        Row({ space: 8 }) {
          Button('添加围栏')
            .layoutWeight(1)
            .onClick(() => {
              this.addFence()
            })

          Button('删除围栏')
            .layoutWeight(1)
            .backgroundColor('#FFF1F0')
            .fontColor('#D4380D')
            .onClick(() => {
              this.removeFence()
            })

          Button(this.isSatellite ? '标准地图' : '卫星地图')
            .layoutWeight(1)
            .onClick(() => {
              this.toggleSatellite()
            })
        }

        Row({ space: 8 }) {
          Button('添加轨迹')
            .layoutWeight(1)
            .onClick(() => {
              this.addTrack()
            })

          Button('删除轨迹')
            .layoutWeight(1)
            .backgroundColor('#FFF1F0')
            .fontColor('#D4380D')
            .onClick(() => {
              this.clearTrack()
            })

          Button('清除路线')
            .layoutWeight(1)
            .backgroundColor('#FFF7E6')
            .fontColor('#D46B08')
            .onClick(() => {
              this.clearRoute()
            })
        }
      }
      .width('100%')
      .padding({ left: 16, right: 16, top: 8, bottom: 24 })
      .backgroundColor(Color.White)
      .borderRadius({ topLeft: 24, topRight: 24 })
      .shadow({ radius: 18, color: '#22000000', offsetX: 0, offsetY: -4 })
      .gesture(
        PanGesture()
      )
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