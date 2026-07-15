export default {
  data() {
    return {
      safeAreaTop: 0,
      safeAreaBottom: 0,
      navBarHeight: 44,
      tabBarHeight: 56
    };
  },
  created() {
    this.initSafeArea();
  },
  methods: {
    initSafeArea() {
      try {
        const systemInfo = uni.getSystemInfoSync();
        const safeAreaInsets = systemInfo.safeAreaInsets || {};
        const top = Number(systemInfo.statusBarHeight || safeAreaInsets.top || 0);
        const bottom = Number(safeAreaInsets.bottom || 0);

        this.safeAreaTop = Math.max(0, top);
        this.safeAreaBottom = Math.max(0, bottom);
        this.navBarHeight = this.safeAreaTop + 44;
        this.tabBarHeight = this.safeAreaBottom + 56;
      } catch (err) {
        this.safeAreaTop = 0;
        this.safeAreaBottom = 0;
        this.navBarHeight = 44;
        this.tabBarHeight = 56;
      }
    }
  }
};
