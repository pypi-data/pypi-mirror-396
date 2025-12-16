
# 这个脚本的任务 是实现倒计时30S关机
# 要求倒计时的时间是易于更改的 
# 要求每一秒的倒计时 是通过弹出的窗口 同步通知给用户的 
# 要求完全的异常处理 用户执行CTRL+C 只有直接退出程序 而不能弹出错误窗口 

# 配置倒计时秒数（易于修改）
$countdownSeconds = 30

# 加载必要的程序集
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 全局变量用于窗体
$script:form = $null
$script:cancelled = $false

try {
    # 创建通知窗体
    $form = New-Object System.Windows.Forms.Form
    $form.FormBorderStyle = 'None'
    $form.BackColor = 'Black'
    $form.ForeColor = 'White'
    $form.TopMost = $true
    $form.StartPosition = 'Manual'
    $form.Size = New-Object System.Drawing.Size(300, 100)
    $form.Location = New-Object System.Drawing.Point(([System.Windows.Forms.Screen]::PrimaryScreen.WorkingArea.Width - 300), 50)
    
    $label = New-Object System.Windows.Forms.Label
    $label.AutoSize = $false
    $label.Dock = 'Fill'
    $label.TextAlign = 'MiddleCenter'
    $label.Font = New-Object System.Drawing.Font("Microsoft YaHei", 12, [System.Drawing.FontStyle]::Bold)
    $form.Controls.Add($label)
    
    $form.Show()
    
    for ($i = $countdownSeconds; $i -gt 0; $i--) {
        if ($script:cancelled) { break }
        $label.Text = "系统将在 $i 秒后关机"
        [System.Windows.Forms.Application]::DoEvents()
        
        # 分段 Sleep 以便更快响应 Ctrl+C
        for ($j = 0; $j -lt 10; $j++) {
            Start-Sleep -Milliseconds 100
            [System.Windows.Forms.Application]::DoEvents()
        }
    }
    
    $form.Close()
    $form.Dispose()
    Stop-Computer -Force
}
catch [System.Management.Automation.PipelineStoppedException] {
    # Ctrl+C 被按下，静默退出
    $script:cancelled = $true
}
catch {
    # 捕获其他异常，静默退出
    $script:cancelled = $true
}
finally {
    if ($form) { 
        $form.Dispose()
    }
}
