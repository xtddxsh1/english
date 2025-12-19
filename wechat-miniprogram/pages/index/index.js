const API_BASE = 'https://your-api.example.com'; // 修改为部署的后端域名

Page({
  data: {
    essay: '',
    result: null,
    rubricList: [],
    loading: false,
  },

  onInput(e) {
    this.setData({ essay: e.detail.value });
  },

  submit() {
    const essay = this.data.essay.trim();
    if (!essay) {
      wx.showToast({ title: '请输入作文', icon: 'none' });
      return;
    }

    this.setData({ loading: true, result: null, rubricList: [] });
    wx.request({
      url: `${API_BASE}/score`,
      method: 'POST',
      data: { essay },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200 && res.data) {
          const rubric = res.data.rubric || {};
          const rubricList = Object.keys(rubric).map((key) => ({
            key,
            ...rubric[key],
          }));
          this.setData({ result: res.data, rubricList });
        } else {
          wx.showToast({ title: '评分失败，请稍后重试', icon: 'none' });
        }
      },
      fail: () => {
        wx.showToast({ title: '网络异常', icon: 'none' });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  }
});
