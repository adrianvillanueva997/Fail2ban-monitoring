pub trait DatabaseDriver {
    fn connect(&self);
    fn close(&self);
}
