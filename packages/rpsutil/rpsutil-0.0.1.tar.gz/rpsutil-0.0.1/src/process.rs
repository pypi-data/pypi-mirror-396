use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use sysinfo::{get_current_pid, Pid, ProcessesToUpdate, System};

#[pyclass]
pub struct Process {
    pid: Pid,
}

#[pymethods]
impl Process {
    #[new]
    #[pyo3(signature = (pid=None))]
    fn new(pid: Option<u32>) -> PyResult<Self> {
        match pid {
            Some(pid) => Ok(Process{pid: Pid::from_u32(pid)}),
            None => {
                let pid = get_current_pid()
                    .map_err(|e| PyRuntimeError::new_err(
                            format!("cannot get pid: {}", e)
                    ))?;
                Ok(Process{pid})
            }
        }
    }

    pub fn pid(&self) -> u32 {
        self.pid.as_u32()
    }

    pub fn kill(&self) {
        let s = System::new_all();
        if let Some(process) = s.process(Pid::from(self.pid)) {
            process.kill();
        }
    }

    #[pyo3(signature = (recursive=false))]
    pub fn children(&self, recursive: bool) -> PyResult<Vec<Process>> {
        let mut sys = System::new();
        sys.refresh_processes(ProcessesToUpdate::All, true);

        let processes = sys.processes();
        let mut descendants = processes
            .values()
            .filter(|p|
                p.parent().is_some() &&
                p.parent().unwrap() == self.pid
            )
            .collect::<Vec<&sysinfo::Process>>();

        if !recursive {
            return Ok(descendants.iter()
                .map(|id| Process{pid: id.pid()})
                .collect::<Vec<Process>>());
        }

        let mut children = Vec::new();
        while let Some(p) = descendants.pop() {
            children.push(Process{pid: p.pid()});

            for (&child_pid, child_proc) in processes {
                if child_pid == p.pid() {
                    descendants.push(child_proc);
                }
            }
        }

        Ok(children)
    }
}
